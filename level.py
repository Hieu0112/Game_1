import pygame
import button
import csv

pygame.init()

clock = pygame.time.Clock()
FPS = 60

#game window
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 640
LOWER_MARGIN = 100
SIDE_MARGIN = 300

screen = pygame.display.set_mode((SCREEN_WIDTH + SIDE_MARGIN, SCREEN_HEIGHT + LOWER_MARGIN))
pygame.display.set_caption('Level Game')


#Các biến cục bộ
ROWS = 16
MAX_COLS = 150
TILE_SIZE = SCREEN_HEIGHT // ROWS
TILE_TYPES = 21
level = 1
MAX_LEVEL = 6
current_tile = 0
scroll_left = False
scroll_right = False
scroll = 0
scroll_speed = 1


#Load các hình ảnh background của map 
pine1_img = pygame.image.load('imageS/Background/pine1.png').convert_alpha()
pine2_img = pygame.image.load('imageS/Background/pine2.png').convert_alpha()
mountain_img = pygame.image.load('imageS/Background/mountain.png').convert_alpha()
sky_img = pygame.image.load('imageS/Background/sky_cloud.png').convert_alpha()
#Load 1 list các khổi ảnh là các vật phẩm ,nhân vật ,...
img_list = []
for x in range(TILE_TYPES):
	img = pygame.image.load(f'imageS/tile/{x}.png').convert_alpha()
	img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
	img_list.append(img)
# Load hình ảnh của 2 nút chính là save và load 
save_img = pygame.image.load('imageS/save_btn.png').convert_alpha()
load_img = pygame.image.load('imageS/load_btn.png').convert_alpha()


#Các biến toàn cục :màu
GREEN = (144, 201, 120)
WHITE = (255, 255, 255)
RED = (200, 25, 25)

#Kiểu chữ
font = pygame.font.SysFont('Futura', 30)

#Tạo 1 list data có độ width và height trùng với giao diện của game chính
world_data = []
for row in range(ROWS):
	r = [-1] * MAX_COLS
	world_data.append(r)

#create ground
for tile in range(0, MAX_COLS):
	world_data[ROWS - 1][tile] = 0


#Hiển thị lên màn hình chính
def draw_text(text, font, text_col, x, y):
	img = font.render(text, True, text_col)
	screen.blit(img, (x, y))


#Tạo background để loại bỏ chuyển động cũ khi di chuyển
def draw_bg():
	screen.fill((161,84,52))
	width = sky_img.get_width()
	for x in range(4):
		screen.blit(sky_img, ((x * width) - scroll * 0.5, 0))
		screen.blit(mountain_img, ((x * width) - scroll * 0.6, SCREEN_HEIGHT - mountain_img.get_height() - 300))
		screen.blit(pine1_img, ((x * width) - scroll * 0.7, SCREEN_HEIGHT - pine1_img.get_height() - 150))
		screen.blit(pine2_img, ((x * width) - scroll * 0.8, SCREEN_HEIGHT - pine2_img.get_height()))

#Tạo các ô mỗi để phục vụ cho việc để các tile vào dễ dàng hơn
def draw_grid():
	#	Vẽ các cột
	for c in range(MAX_COLS + 1):
		pygame.draw.line(screen, WHITE, (c * TILE_SIZE - scroll, 0), (c * TILE_SIZE - scroll, SCREEN_HEIGHT))
	# 	Vẽ các hàng
	for c in range(ROWS + 1):
		pygame.draw.line(screen, WHITE, (0, c * TILE_SIZE), (SCREEN_WIDTH, c * TILE_SIZE))


# load thế giới của game ứng với các file để chỉnh sửa 
def draw_world():
	for y, row in enumerate(world_data):
		for x, tile in enumerate(row):
			if tile >= 0:
				screen.blit(img_list[tile], (x * TILE_SIZE - scroll, y * TILE_SIZE))



#Tạo 2 nút chính
save_button = button.Button(SCREEN_WIDTH // 2, SCREEN_HEIGHT + LOWER_MARGIN - 50, save_img, 1)
load_button = button.Button(SCREEN_WIDTH // 2 + 200, SCREEN_HEIGHT + LOWER_MARGIN - 50, load_img, 1)
#Danh sách các nút ứng với các tile để tạo map
button_list = []
button_col = 0
button_row = 0
for i in range(len(img_list)):
	tile_button = button.Button(SCREEN_WIDTH + (75 * button_col) + 50, 75 * button_row + 50, img_list[i], 1)
	button_list.append(tile_button)
	button_col += 1
	if button_col == 3:
		button_row += 1
		button_col = 0
run = True
while run:

	if level == MAX_LEVEL + 1 :
		level = 1
	clock.tick(FPS)

	draw_bg()
	draw_grid()
	draw_world()

	draw_text(f'Level current: {level}/{MAX_LEVEL}', font, WHITE, 10, SCREEN_HEIGHT + LOWER_MARGIN - 90)
	draw_text('Press W or S to change level', font, WHITE, 10, SCREEN_HEIGHT + LOWER_MARGIN - 60)

	#Nếu chọn nút save thì dữ liệu sẽ ghi vào file
	if save_button.draw(screen):
		#save level data
		with open(f'level{level}_data.csv', 'w', newline='') as csvfile:
			writer = csv.writer(csvfile, delimiter = ',')
			for row in world_data:
				writer.writerow(row)
	#Nếu chọn nút load dữ liệu sẽ load từ file vào
	if load_button.draw(screen):
		scroll = 0
		with open(f'level{level}_data.csv', newline='') as csvfile:
			reader = csv.reader(csvfile, delimiter = ',')
			for x, row in enumerate(reader):
				for y, tile in enumerate(row):
					world_data[x][y] = int(tile)
				

	#draw tile panel and tiles
	pygame.draw.rect(screen, (161,84,52), (SCREEN_WIDTH, 0, SIDE_MARGIN, SCREEN_HEIGHT))

	#Chọn nút nào thì nút đó sẽ hiển thị viền đỏ đế xác nhận đã chọn
	# enumerate : đánh dấu STT của các nút->(index ,value)
	button_count = 0
	for button_count, i in enumerate(button_list):
		if i.draw(screen):
			current_tile = button_count
	pygame.draw.rect(screen, RED, button_list[current_tile].rect, 2)

	# cuộn màn hình
	if scroll_left == True and scroll > 0:
		scroll -= 5 * scroll_speed
	if scroll_right == True and scroll < (MAX_COLS * TILE_SIZE) - SCREEN_WIDTH:
		scroll += 5 * scroll_speed

	pos = pygame.mouse.get_pos()
	x = (pos[0] + scroll) // TILE_SIZE
	y = pos[1] // TILE_SIZE

	#kiểm tra có đang chọn ở vùng tile không nếu có thì mới có thể hiển thị ở map
	if pos[0] < SCREEN_WIDTH and pos[1] < SCREEN_HEIGHT:
		#Cập nhật giá trị
		# Kiểm tra bấm chuột trái thì thêm giá trị  
		if pygame.mouse.get_pressed()[0] == 1:
			world_data[y][x] = current_tile
		# Chuột phải thì xóa giá trị
		if pygame.mouse.get_pressed()[2] == 1:
			world_data[y][x] = -1

	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			run = False
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_w:
				level += 1
			if event.key == pygame.K_s and level > 0:
				level -= 1
			if event.key == pygame.K_a:
				scroll_left = True
			if event.key == pygame.K_d:
				scroll_right = True

		if event.type == pygame.KEYUP:
			if event.key == pygame.K_a:
				scroll_left = False
			if event.key == pygame.K_d:
				scroll_right = False

	pygame.display.update()
pygame.quit()