import pygame
from pygame import mixer
import os
import random
import csv
import button

"""
Ox -> truc dương Ox
oy -> trục âm của Oy
Va chạm trên các hình chữ nhật -> các khối nhân vật ,đạn ,hộp ,đá ,...
cách biểu diễn 1:rect(x, y, width, height)
Cách biểu diễn 2:(x1, y1, x2, y2)
	x1 là hoành độ điểm trên cùng bên trái.
	y1 là tung độ điểm trên cùng bên trái.
	x2 là hoành độ điểm dưới cùng bên phải.
	y2 là tung độ điểm dưới cùng bên phải.
Mối liên hệ
x1 = x
y1 = y
x2 = x + width
y2 = y + height

collision(surface1,pos1,surface2,pos2) -> Hàm kiểm tra va chạm
pos1 dạng (x,y) : là vị trí của surface1
pos2 dạng (x,y) : là vị trí của surface2

"""
mixer.init()
pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT= int(SCREEN_WIDTH * 0.8)

screen=pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
pygame.display.set_caption('Shooter')

# Cài đặt tốc độ khung hình
clock=pygame.time.Clock()
FPS=60

# Các biến toàn cục được sử dụng trong game
GRAVITY=0.75
SCROOL_THRESH = 200
ROWS = 16
COLS = 150
# Kích thức 1 ô
TILE_SIZE = SCREEN_HEIGHT // ROWS
TILE_TYPES = 21
MAX_LEVELS = 6
ENEMY_NEED = 0
ENEMY_CURRENT = 0
screen_scroll = 0
bg_scroll = 0
level = 1
start_game = False
start_intro = False

# Các biến xác định hành động của nhân vật 
moving_left = False
moving_right = False
shoot = False
grenade = False
grenade_thrown = False


# Load âm thanh
# âm thanh game
pygame.mixer.music.load('audio/music2.mp3')
pygame.mixer.music.set_volume(0.1)
# Lap vo han ,vi tri bat dau phat ,am nhac mờ dần đến time(mms) 0.0 : bỏ qua 
pygame.mixer.music.play(-1 ,0.0,5000)
# âm thanh nhảy
jum_fx = pygame.mixer.Sound('audio/jump.wav')
jum_fx.set_volume(0.05)
# Âm thanh bắn
shot_fx = pygame.mixer.Sound('audio/shot.wav')
shot_fx.set_volume(0.05)
# Âm thanh lựu đạn
grenade_fx = pygame.mixer.Sound('audio/grenade.wav')
grenade_fx.set_volume(0.05)

# Load các image , loại bỏ background ,vẽ nhanh hơn
# Load hình ảnh 3 nút : start - exit - restart
start_img=pygame.image.load('img/start_btn.png').convert_alpha()
exit_img=pygame.image.load('img/exit_btn.png').convert_alpha()
restart_img=pygame.image.load('img/restart_btn.png').convert_alpha()
# Load background 
pine1_img=pygame.image.load('img/Background/pine1.png').convert_alpha()
pine2_img=pygame.image.load('img/Background/pine2.png').convert_alpha()
mountain_img=pygame.image.load('img/Background/mountain.png').convert_alpha()
sky_img=pygame.image.load('img/Background/sky_cloud.png').convert_alpha()
# Lưu các khối trong danh sách
img_list = []
for x in range(TILE_TYPES):
	img = pygame.image.load(f'img/Tile/{x}.png')
	img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
	img_list.append(img)

# Load hình ảnh đạn :bullet
bullet_img=pygame.image.load('img/icons/bullet.png').convert_alpha()
# Load hình ảnh lựu đạn :grenade
grenade_img=pygame.image.load('img/icons/grenade.png').convert_alpha()
# Load hình ảnh 3 loại hộp vật phẩm : máu ,đạn ,lựu đạn 
health_box_img = pygame.image.load('img/icons/health_box.png').convert_alpha()
ammo_box_img = pygame.image.load('img/icons/ammo_box.png').convert_alpha()
grenade_box_img = pygame.image.load('img/icons/grenade_box.png').convert_alpha()
special_box_img = pygame.image.load('img/icons/special.png').convert_alpha()
item_boxes = {
	'Health' : health_box_img,
	'Ammo' : ammo_box_img,
	'Grenade' :grenade_box_img,
	'Special' : special_box_img,
}

# Biến màu sắc và kiểu chữ mặc định
font = pygame.font.SysFont('Futura' ,30)
font_lv = pygame.font.SysFont('Arial' ,40)
BG=(161,84,52)
RED=(255,0,0)
WHITE = (255 ,255, 255)
GREEN = (0 ,255,0)
BLACK = (0, 0, 0)
PINK= (235, 65,54)

def draw_text(text, font, text_col ,x ,y):
	img = font.render(text, True ,text_col)
	screen.blit(img, (x, y))

# Hiển thị hình nền 
def draw_bg():
	screen.fill(BG)
	width = sky_img.get_width()
	for x in range(5):
		screen.blit(sky_img, ((x*width) - bg_scroll * 0.5, 0))
		screen.blit(mountain_img ,((x*width) - bg_scroll * 0.6, SCREEN_HEIGHT - mountain_img.get_height() -300))
		screen.blit(pine1_img , ((x*width) - bg_scroll * 0.7, SCREEN_HEIGHT - pine1_img.get_height() - 150))
		screen.blit(pine2_img , ((x*width) - bg_scroll * 0.8, SCREEN_HEIGHT - pine2_img.get_height() ))

# reset lại mọi thứ trở về như bắt đầu game : khi chết máu về 0 -> reset 
def reset_level():
	enemy_group.empty()
	enemy_dead_group.empty()
	bullet_group.empty()
	grenade_group.empty()
	explosion_group.empty()
	item_box_group.empty()
	decoration_group.empty()
	water_group.empty()
	exit_group.empty()

	# create empty tile list 
	data = []
	for _ in range(ROWS):
		r =[-1] * COLS
		data.append(r)

	return data

# class Người 
class Soldier(pygame.sprite.Sprite):
	def __init__(self, char_type, x, y, scale, speed, ammo ,grenades):
		pygame.sprite.Sprite.__init__(self)
		self.x = x
		self.y = y
		# Người chơi còn sống
		self.alive = True
		# Khởi tạo enemy hay player
		self.char_type = char_type
		# Tốc độ di chuyển
		self.speed = speed
		# Bao nhiêu viên đạn
		self.ammo = ammo
		self.start_ammo = ammo
		# Tốc độ bắn đạn
		self.shoot_cooldown = 0
		# Bao nhiêu trái lựu đạn
		self.grenades = grenades
		# Máu người chơi
		self.health = 100
		# Máu tối đa của người chơi
		self.max_health = self.health
		# Hướng của nhân vật -> phải :1 trái :-1
		self.direction = 1
		#vận tốc theo trục y
		self.vel_y = 0
		# Biến nhảy
		self.jump = False
		# check xem có đang nhảy hay không nếu đang nhảy thì không được nhảy tiếp
		self.in_air = True
		self.flip = False
		self.animation_list = []
		self.frame_index = 0
		self.action = 0
		self.update_time = pygame.time.get_ticks()
		#Biến cho AI -> các enemy
		self.move_counter = 0
		self.vision = pygame.Rect(0, 0, 150 + level * 2, 20 + level )
		self.idling = False
		self.idling_counter = 0
		#Load các ảnh cho chuyển động của nhân vật 
		animation_type=['Idle', 'Run', 'Jump', 'Death']
		for animation in animation_type:	
			temp_list = []
			# Đếm xem có tât cả bao nhiêu ảnh trong folder image
			num_of_frames = len(os.listdir(f'img/{self.char_type}/{animation}'))
			for i in range(num_of_frames):
				img=pygame.image.load(f'img/{self.char_type}/{animation}/{i}.png').convert_alpha()
				img=pygame.transform.scale(img,(int(img.get_width()*scale),int(img.get_height()*scale)))
				temp_list.append(img)
			self.animation_list.append(temp_list)

		self.image = self.animation_list[self.action][self.frame_index]	
		self.rect = self.image.get_rect()
		self.rect.center = (x,y)
		self.width = self.image.get_width()
		self.height = self.image.get_height()
	

	def update(self):
		self.update_animation()
		self.check_alive()
		if self.shoot_cooldown > 0 :
			self.shoot_cooldown -= 1


	def move(self,moving_left,moving_right):
		screen_scroll = 0
		# Độ di chuyển = 0
		dx=0
		dy=0

		#assign movement variables if moving left or right
		if moving_left :
			dx = -self.speed
			#Nếu di chuyển sang trái thì lật ảnh quay trái
			self.flip = True
			self.direction = -1

		if moving_right:
			dx = self.speed
			#di chuyển sang phải thì lậi ảnh quay phải
			self.flip = False
			self.direction = 1
		
		#jump -> Chỉ được nhảy 1 lần duy nhất
		if self.jump == True and self.in_air == False:
			self.vel_y = -12
			self.jump = False
			self.in_air = True

		#Áp dụng trọng lực
		self.vel_y += GRAVITY
		dy += self.vel_y

		#kiểm tra va chạm của các hình chữ nhật
		for tile in world.obstacle_list:
			#kiểm tra va chạm theo trục x
			if tile[1].colliderect(self.rect.x + dx ,self.rect.y ,\
			  self.width, self.height):
				dx = 0
				# if the ai has hit a wall then make it turn around
				if self.char_type == 'enemy':
					self.direction *= -1
					self.move_counter = 0
			#kiểm tra va chạm theo trục y
			if tile[1].colliderect(self.rect.x ,self.rect.y + dy,\
			  self.width, self.height):
				#kiểm tra nếu dưới mặt đất (tức là đang nhảy)
				if self.vel_y < 0 :
					self.vel_y = 0
					dy = tile[1].bottom - self.rect.top
				#kiểm tra ở trên mặt đất ( tức là đang rơi)
				elif self.vel_y >= 0:
					self.vel_y = 0
					self.in_air = False
					dy = tile[1].top - self.rect.bottom

		#Kiểm tra va chạm nước
		# check xem self có va chạm với khối water_group không -> Nếu chạm sẽ chết và sẽ không xóa đi khối nước
		if pygame.sprite.spritecollide(self, water_group, False):
			self.health = 0

		#kiểm tra chạm khối exit : hoan thanh game
		level_complete = False
		if pygame.sprite.spritecollide(self, exit_group, False):
			level_complete = True

		#Kiểm tra rơi khỏi map
		if self.rect.bottom > SCREEN_HEIGHT:
			self.health = 0

		#kiểm tra chạm viền màn hình
		if self.char_type == 'player':
			if self.rect.left + dx < 0 or self.rect.right + dx > SCREEN_WIDTH :
				dx = 0

		# update vị trí Hình chữ nhật _ nhân vật 
		self.rect.x += dx
		self.rect.y += dy

		#cập nhật cuộn màn hình dựa trên vị trí của người chơi
		if self.char_type == 'player':
			if (self.rect.right > SCREEN_WIDTH - SCROOL_THRESH and bg_scroll < ( world.level_length * TILE_SIZE) - SCREEN_WIDTH)\
				or (self.rect.left < SCROOL_THRESH and bg_scroll > abs(dx)):
				self.rect.x -= dx
				screen_scroll = -dx

		return screen_scroll ,level_complete

	def ai(self):
		#địch tuần tra
		if self.alive and player.alive :
			#Dùng hàm random để tránh
			# đứng lại nghỉ ngơi
			if self.idling == False and random.randint(1,200) == 1:
				self.update_action(0)
				# Việc tất cả đều hành động giống nhau
				self.idling = True 
				# time đứng lại nghỉ ngơi
				self.idling_counter = 45
			#kiểm tra người chơi có trong tầm nhìn của địch không
			if self.vision.colliderect(player.rect):
				#stop running and face the player
				self.update_action(0)
				self.shoot()
			else :
				if self.idling == False:
					if self.direction == 1 :
						ai_moving_right = True
					else :
						ai_moving_right = False
					ai_moving_left = not ai_moving_right
					self.move(ai_moving_left ,ai_moving_right)
					self.update_action(1)
					self.move_counter += 1
					#cập nhật tầm nhìn khi địch di chuyển
					self.vision.center = (self.rect.centerx + 75 * self.direction\
					,self.rect.centery)

					if self.move_counter > int(TILE_SIZE * 0.9):
						self.direction *= -1
						self.move_counter *= -1
				else:
					self.idling_counter -= 1
					if self.idling_counter <= 0:
						self.idling = False	

		# Cuộn màn hình cập nhật vị trí của AI theo người chơi 
		self.rect.x += screen_scroll

	def shoot(self):
		if self.shoot_cooldown == 0 and self.ammo > 0:
			# cài đặt tôc độ bắn của nhân vật và địch
			self.shoot_cooldown = 25
			if self.char_type == 'enemy':
				self.shoot_cooldown = 60 - level * 5
			bullet = Bullet(self.rect.centerx + (0.75 * self.rect.size[0] * self.direction)\
		   , self.rect.centery, self.direction)
			bullet_group.add(bullet)
			# Khi bắn giảm đạn đi 1 viên
			self.ammo -= 1
			shot_fx.play()

	# Update hiệu ứng các ảnh
	def update_animation(self):
		# Thời gian chuyển tiếp của các ảnh
		ANIMATION_COOLDOWN = 100
		#update image depending on current frame
		self.image = self.animation_list[self.action][self.frame_index]
		#check if enough time has passed since the last update
		if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
			self.update_time = pygame.time.get_ticks()
			self.frame_index += 1 
		#if the animation has run out the reset back to the start
		if self.frame_index >=len(self.animation_list[self.action]):
			if self.action == 3:
				self.frame_index = len(self.animation_list[self.action]) - 1
			else :
				self.frame_index = 0


	def update_action(self,new_action):
		#check if the new action is different to the previous one
		if new_action != self.action:
			self.action = new_action
			#update the animation settings
			self.frame_index = 0
			self.update_time = pygame.time.get_ticks()
	# Nếu người chơi chết thì đặt sang trạng thái đã chết : hình ảnh nằm xuống
	def check_alive(self):
		if self.health <= 0:
			self.health = 0
			self.speed = 0
			self.alive = False
			self.update_action(3)
			if self.char_type == 'enemy':
				enemy_dead_group.remove(self)


	def draw(self):
		screen.blit(pygame.transform.flip(self.image , self.flip,False), self.rect)

# Tạo dữ liệu thế giới -> Load nhân vật ,enemy , vật phẩm ,quang cảnh ,...
class World():
	def __init__(self):
		# Danh sách các ô đất để di chuyển
		self.obstacle_list = []
	
	def process_data(self, data):
		self.level_length = len(data[0])
		#lặp qua từng giá trị trong tệp dữ liệu cấp độ
		for y, row in enumerate(data):
			for x, tile in enumerate(row):
				if tile >= 0:
					img = img_list[tile]
					img_rect = img.get_rect()
					img_rect.x = x * TILE_SIZE
					img_rect.y = y * TILE_SIZE
					# Ảnh hình chữ nhật -> các ô đất
					tile_data = (img, img_rect)
					if tile >= 0 and tile <= 8:
						self.obstacle_list.append(tile_data)
					# Nước
					elif tile >= 9 and tile <= 10:
						water = Water(img,x * TILE_SIZE, y * TILE_SIZE)
						water_group.add(water)
					# Cỏ , đá
					elif tile >=11 and tile <=14 and tile !=12:
						decoration = Decoration(img,x * TILE_SIZE, y * TILE_SIZE)
						decoration_group.add(decoration)
					elif tile == 12:
						item_box = ItemBox('Special',x * TILE_SIZE, y * TILE_SIZE)
						item_box_group.add(item_box)
					# Tạo người chơi
					elif tile == 15:
						player = Soldier('player', x * TILE_SIZE, y * TILE_SIZE, 1.6, 5, 20, 5)
						health_bar =  HealthBar(10 ,10 ,player.health ,player.max_health)
					# Tạo địch
					elif tile == 16: 
						enemy = Soldier('enemy', x * TILE_SIZE, y * TILE_SIZE, 1.6, 1 + level//2, 100, 0)
						enemy_group.add(enemy)
						enemy_dead_group.add(enemy)
					# Tạo hộp đạn
					elif tile == 17:
						item_box = ItemBox('Ammo',x * TILE_SIZE, y * TILE_SIZE)
						item_box_group.add(item_box)
					# Tạo hộp lựu đạn
					elif tile == 18:
						item_box = ItemBox('Grenade',x * TILE_SIZE, y * TILE_SIZE)
						item_box_group.add(item_box)
					# Tạo hộp máu
					elif tile == 19:
						item_box = ItemBox('Health',x * TILE_SIZE, y * TILE_SIZE)
						item_box_group.add(item_box)
					# Thoát
					elif tile == 20:
						exit = Exit(img,x * TILE_SIZE, y * TILE_SIZE)
						exit_group.add(exit)
		return player ,health_bar
	
	def draw(self):
		for tile in self.obstacle_list:
			tile[1][0] += screen_scroll
			screen.blit(tile[0] ,tile[1])

""" 3 lớp dưới có code giống nhau nhưng 
phải chia ra vì nó tương tác khác nhau với người chơi"""

# Cac khoi da , co ,...
class Decoration(pygame.sprite.Sprite):
	def __init__(self,img ,x, y):
		pygame.sprite.Sprite.__init__(self)
		self.image = img
		self.rect = self.image.get_rect()
		self.rect.midtop = (x + TILE_SIZE // 2 ,y + (TILE_SIZE - self.image.get_height()))
	
	def update(self):
		self.rect.x += screen_scroll

# Nuoc
class Water(pygame.sprite.Sprite):
	def __init__(self,img ,x, y):
		pygame.sprite.Sprite.__init__(self)
		self.image = img
		self.rect = self.image.get_rect()
		self.rect.midtop = (x + TILE_SIZE // 2 ,y + (TILE_SIZE - self.image.get_height()))

	def update(self):
		self.rect.x += screen_scroll

# Khoi exit
class Exit(pygame.sprite.Sprite):
	def __init__(self,img ,x, y):
		pygame.sprite.Sprite.__init__(self)
		self.image = img
		self.rect = self.image.get_rect()
		self.rect.midtop = (x + TILE_SIZE // 2 ,y + (TILE_SIZE - self.image.get_height()))
	
	def update(self):
		self.rect.x += screen_scroll


# Lớp các hộp 
class ItemBox(pygame.sprite.Sprite):
	def __init__(self,item_type ,x, y):
		pygame.sprite.Sprite.__init__(self)
		self.item_type = item_type
		self.image = item_boxes[self.item_type]
		self.rect = self.image.get_rect()
		self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

	def update(self):
		# scroll
		self.rect.x += screen_scroll
		# kiểm tra người chơi nhặt hộp
		if pygame.sprite.collide_rect(self, player):
			# Nhặt máu : máu = min(100 ,player.health)
			if self.item_type == 'Health':
				player.health += 25
				if player.health > player.max_health:
					player.health = player.max_health
			# Nhặt đạn
			elif self.item_type == 'Ammo':
				player.ammo += 15
				if player.ammo >= 25:
					player.ammo = 25
			# Nhặt lựu đạn
			elif self.item_type == 'Grenade':
				player.grenades += 3
				if player.grenades >= 10:
					player.grenades = 10
			# Nhặt hộp đặc biệt
			elif self.item_type == 'Special':
				rd = random.randint(1,4)
				if rd == 1 :
					player.health += random.randint(10,20)
					if player.health > player.max_health:
						player.health = player.max_health
				elif rd == 2 :
					player.ammo += random.randint(8,15)
					if player.ammo >= 25:
						player.ammo = 25
				elif rd == 3 :
					player.grenades += random.randint(1,3)
					if player.grenades >= 10:
						player.grenades = 10
				else :
					player.health -= random.randint(20,30)
			# Sau khi nhặt thì xóa hộp đã nhặt
			self.kill()
# Thanh máu
class HealthBar():
	def __init__(self ,x, y ,health ,max_health):
		self.x = x
		self.y = y
		self.health = health
		self.max_health = max_health
	
	def draw(self ,health):
		#update with new health
		self.health = health
		#calculate health ratio
		ratio = self.health / self.max_health
		pygame.draw.rect(screen, BLACK , (self.x - 2, self.y - 2 ,154 ,24))
		pygame.draw.rect(screen, RED , (self.x, self.y ,150 ,20))
		pygame.draw.rect(screen, GREEN , (self.x, self.y ,150 * ratio ,20))
# Lớp đạn 
class Bullet(pygame.sprite.Sprite):
	def __init__(self,x,y,direction):
		pygame.sprite.Sprite.__init__(self)
		self.speed = 10
		self.image=bullet_img
		self.rect = self.image.get_rect()
		self.rect.center = (x, y)
		self.direction = direction

	def update(self):
		# Di chuyển đạn
		self.rect.x += (self.speed * self.direction) + screen_scroll
		# Xoá đạn nếu ra khỏi ngoài màn hình nếu không ko nó vẫn tồn tại trong bộ nhớ
		if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH :
			self.kill()
		#kiểm tra va chạm đạn với vật cản
		for tile in world.obstacle_list:
			if tile[1].colliderect(self.rect):
				self.kill()
		#Nếu đạn va chạm với người chơi trừ 5 máu
		if pygame.sprite.spritecollide(player, bullet_group ,False):
			if player.alive:
				player.health -= (5 + level)
				self.kill()
		#Nếu đạn va chạm với người enemy trừ 25 máu
		for enemy in enemy_group:
			if pygame.sprite.spritecollide(enemy, bullet_group ,False):
				if enemy.alive:
					enemy.health -= 25
					self.kill()

# Lớp lựu đạn 
class Grenade(pygame.sprite.Sprite):
	def __init__(self, x, y, direction):
		pygame.sprite.Sprite.__init__(self)
		self.timer = 100
		self.vel_y = -11
		self.speed = 7
		self.image = grenade_img
		self.rect  = self.image.get_rect()
		self.rect.center = (x, y)
		self.width = self.image.get_width()
		self.height = self.image.get_height()
		self.direction = direction
	
	def update(self):
		self.vel_y += GRAVITY
		dx = self.direction * self.speed
		dy = self.vel_y 
		#kiểm tra va chạm vật cản
		for tile in world.obstacle_list:
			# va chạm với tường
			if tile[1].colliderect(self.rect.x + dx,self.rect.y, \
			  self.width, self.height):
				self.direction *= -1
				dx = self.direction * self.speed
			# Kiểm tra va chạm theo trục y
			if tile[1].colliderect(self.rect.x ,self.rect.y + dy,\
			  self.width, self.height):
				#kiểm tra nếu dưới mặt đất (tức là lựu đạn đang bay lên)
				self.speed = 0
				if self.vel_y < 0 :
					self.vel_y = 0
					dy = tile[1].bottom - self.rect.top
				#kiểm tra ở trên mặt đất ( tức là đang rơi)
				elif self.vel_y >= 0:
					self.vel_y = 0
					dy = tile[1].top - self.rect.bottom

		# update grenade position
		self.rect.x += dx + screen_scroll
		self.rect.y += dy

		# Nổ
		self.timer -= 1
		if self.timer <= 0 :
			self.kill()
			grenade_fx.play()
			explosion = Explosion(self.rect.x ,self.rect.y ,0.5)
			explosion_group.add(explosion)
			#Gây sát thương trong bán kính
			if abs(self.rect.centerx - player.rect.centerx) < TILE_SIZE * 2 and \
				abs(self.rect.centery - player.rect.centery) < TILE_SIZE * 2:
				player.health -= 50
			for enemy in enemy_group:
				if abs(self.rect.centerx - enemy.rect.centerx) < TILE_SIZE * 2 and \
					abs(self.rect.centery - enemy.rect.centery) < TILE_SIZE * 2:
					enemy.health -= 50

# Lớp đạn nổ 
class Explosion(pygame.sprite.Sprite):
	def __init__(self, x, y, scale):
		pygame.sprite.Sprite.__init__(self)
		self.images = []
		for num in range(1,6):
			img = pygame.image.load(f'img/explosion/exp{num}.png').convert_alpha()
			img = pygame.transform.scale(img, (int(img.get_width() * scale),int(img.get_height() * scale)))
			self.images.append(img)
		self.frame_index = 0
		self.image = self.images[self.frame_index]
		self.rect  = self.image.get_rect()
		self.rect.center = (x, y)
		self.counter = 0

	def update(self):
		# scroll
		self.rect.x += screen_scroll
		EXPLOSION_SPEED = 4
		# update explosion animation
		self.counter += 1
		if self.counter >= EXPLOSION_SPEED:
			self.counter = 0
			self.frame_index += 1
			# if the animation is complete then delete the Explosion
			if self.frame_index >= len(self.images):
				self.kill()
			else:
				self.image = self.images[self.frame_index]

# Lớp tạo hiệu ứng chải màn khi chết hay vào start
class ScreenFade():
	def __init__(self ,direction ,color ,speed):
		self.direction = direction
		self.color = color
		self.speed = speed
		self.fade_counter = 0

	def fade(self):
		fade_complete = False
		self.fade_counter += self.speed
		if self.direction == 1 : #whole screen fade
			pygame.draw.rect(screen, self.color, (0 - self.fade_counter, 0, SCREEN_WIDTH // 2, SCREEN_HEIGHT))
			pygame.draw.rect(screen, self.color, (SCREEN_WIDTH // 2 + self.fade_counter, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
			pygame.draw.rect(screen, self.color, (0, 0 - self.fade_counter, SCREEN_WIDTH, SCREEN_HEIGHT // 2))
			pygame.draw.rect(screen, self.color, (0, SCREEN_HEIGHT // 2 +self.fade_counter, SCREEN_WIDTH, SCREEN_HEIGHT))
		if self.direction == 2 : #vertical screem fade down
			pygame.draw.rect(screen ,self.color ,(0 ,0, SCREEN_WIDTH ,0 + self.fade_counter))
		if self.fade_counter >= SCREEN_WIDTH :
			fade_complete = True 
		return fade_complete
	
#create screen fades
intro_fade = ScreenFade(1, (225,99,71), 4)
death_fade = ScreenFade(2, (0,128,128), 4)
	
# Tạo 3 nút 
start_button = button.Button(SCREEN_WIDTH // 2 -130 ,SCREEN_HEIGHT // 2 -150 ,start_img, 1)
exit_button = button.Button(SCREEN_WIDTH // 2 -110 ,SCREEN_HEIGHT // 2 +50 ,exit_img, 1)
restart_button = button.Button(SCREEN_WIDTH // 2 -100 ,SCREEN_HEIGHT // 2 - 50 ,restart_img, 1)
# create sprite groups
enemy_group = pygame.sprite.Group()
enemy_dead_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
grenade_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()
item_box_group = pygame.sprite.Group()
decoration_group = pygame.sprite.Group()
water_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()

# Tạo map gồm các ô mỗi ô ứng với giá trị âm 1
world_data = []
for row in range(ROWS):
	r = [-1] * COLS
	world_data.append(r)
#tải dữ liệu và tạo map
with open(f'level{level}_data.csv' ,newline='') as csvfile:
	reader = csv.reader(csvfile , delimiter=',')
	for x, row in enumerate(reader):
		for y, tile in enumerate(row):
			world_data[x][y] = int(tile)

world = World()
player ,health_bar = world.process_data(world_data)

run=True
while run:
	clock.tick(FPS)

	if start_game == False:
		# draw menu
		screen.fill(BG)
		# add buttons
		if start_button.draw(screen) :
			start_game = True
			start_intro = True
		if exit_button.draw(screen) :
			run = False
	else :
		#update background
		draw_bg()
		#draw world map
		world.draw()
		draw_text(f'Level: {level} ',font_lv, RED,340, 0)
		#show player health
		health_bar.draw(player.health)
		#show ammo
		draw_text(f'AMMO: ',font, WHITE, 10, 35)
		for x in range(player.ammo):
			screen.blit(bullet_img , (90 + (x * 10) ,40))
		#show grenades
		draw_text(f'GRENADES:',font, WHITE, 10, 60)
		for x in range(player.grenades):
			screen.blit(grenade_img , (135 + (x * 15) ,60))

		color = RED
		ENEMY_NEED = int(len(enemy_group) * 0.4 + level // 2)
		ENEMY_CURRENT = len(enemy_group) - len(enemy_dead_group)
		if ENEMY_CURRENT >= ENEMY_NEED:
			color = GREEN
		draw_text(f'KIILED:{ENEMY_CURRENT}/{ENEMY_NEED}',font, color, 10, 85)

		player.update()
		player.draw()

		for enemy in enemy_group:
			enemy.ai()
			enemy.update()
			enemy.draw()
		#update and draw groups
		bullet_group.update()
		grenade_group.update()
		explosion_group.update()
		item_box_group.update()
		decoration_group.update()
		water_group.update()
		exit_group.update()

		bullet_group.draw(screen)
		grenade_group.draw(screen)
		explosion_group.draw(screen)
		item_box_group.draw(screen)
		decoration_group.draw(screen)
		water_group.draw(screen)
		exit_group.draw(screen)

		if start_intro == True:
			if intro_fade.fade():
				start_intro = False
				intro_fade.fade_counter = 0


		# Update player actions
		# Nếu người chơi còn sống mới thực thi
		if player.alive:
			if shoot:
				player.shoot()
			#Ném lựu đạn
			elif grenade and grenade_thrown == False and player.grenades > 0:
				grenade=Grenade(player.rect.centerx + (0.5 * player.rect.size[0] * player.direction),\
					player.rect.top ,player.direction)
				grenade_group.add(grenade)
				player.grenades -= 1
				grenade_thrown = True
			# Update image chuyển động của nhân vật khi ở các trạng thái nhảy ,chạy và đứng im
			if player.in_air:
				player.update_action(2)
			elif moving_left or moving_right:
				player.update_action(1)
			else :
				player.update_action(0)
			screen_scroll, level_complete = player.move(moving_left,moving_right)
			bg_scroll -= screen_scroll
			# check if player has completed the level
			if level_complete and ENEMY_CURRENT >= ENEMY_NEED :
				start_intro = True
				level += 1
				bg_scroll = 0
				world_data = reset_level()
				if level == MAX_LEVELS + 1:
					start_game = False
					level = 1
				if level <= MAX_LEVELS :
					with open(f'level{level}_data.csv' ,newline='') as csvfile:
						reader = csv.reader(csvfile , delimiter=',')
						for x, row in enumerate(reader):
							for y, tile in enumerate(row):
								world_data[x][y] = int(tile)
					world = World()
					player ,health_bar = world.process_data(world_data)
		else :
			screen_scroll = 0
			if death_fade.fade():
				if restart_button.draw(screen):
					death_fade.fade_counter = 0
					start_intro = True
					bg_scroll = 0
					world_data = reset_level()
					#Load lại dữ liệu như ban đầu mới vào game
					with open(f'level{level}_data.csv' ,newline='') as csvfile:
						reader = csv.reader(csvfile , delimiter=',')
						for x, row in enumerate(reader):
							for y, tile in enumerate(row):
								world_data[x][y] = int(tile)
					world = World()
					player ,health_bar = world.process_data(world_data)


	for event in pygame.event.get():
		# thoát game
		if event.type == pygame.QUIT:
			run=False
		# Khi nhấn bàn phím
		if event.type== pygame.KEYDOWN:
			# Bấm nút a -> di chuyển sang trái
			if event.key == pygame.K_a:
				moving_left = True
			# Bấm nút d -> di chuyển sang phải
			if event.key == pygame.K_d:
				moving_right = True
			# Bấm nút Space -> bắn
			if event.key == pygame.K_SPACE:
				shoot=True
			# Bấm nút q -> ném nựu đạn
			if event.key == pygame.K_q:
				grenade=True
			# Bấm nút w -> Nhảy lên và có âm thanh nhảy
			if event.key == pygame.K_w and player.alive:
				player.jump = True
				jum_fx.play()
			if event.key == pygame.K_ESCAPE:
				run=False

		#Khi bàn phím được thả
		if event.type == pygame.KEYUP:
			if event.key == pygame.K_a:
				moving_left = False
			if event.key == pygame.K_d:
				moving_right = False
			if event.key == pygame.K_SPACE:
				shoot=False
			if event.key == pygame.K_q:
				grenade=False
				grenade_thrown = False

	pygame.display.update()
pygame.quit()