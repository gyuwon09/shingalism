import sys

import pygame
import cv2
from datetime import datetime
import shutil
from tkinter import messagebox
from func import *
from google_drive import *

pygame.init()

printing = False
on_google = False

class Button:
    def __init__(self, x, y, width, height, color, text):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.text = text
        self.font = font_36
        self.text_surf = self.font.render(text, True, (0, 0, 0))
        self.text_rect = self.text_surf.get_rect(center=self.rect.center)

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        screen.blit(self.text_surf, self.text_rect)

    def is_clicked(self, mouse_pos, mouse_pressed):
        if self.rect.collidepoint(mouse_pos) and mouse_pressed[0]:
            return True
        return False


# OpenCV 카메라 설정
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    raise Exception("카메라를 열 수 없습니다.")

ret, frame = cap.read()
if not ret:
    raise Exception("카메라 프레임을 가져올 수 없습니다.")

frame = cv2.flip(frame, 1)

# 전체화면 모드
screen = pygame.display.set_mode((0, 0))
screen_width, screen_height = screen.get_size()
pygame.display.set_caption("shingalism")

pc_user_name = "user"
font_locate = fr"C:\Users\{pc_user_name}\AppData\Local\Microsoft\Windows\Fonts\Pretendard-SemiBold.otf"
# 폰트
try:
    font_48 = pygame.font.Font(font_locate, 48)
    font_36 = pygame.font.Font(font_locate, 36)
except:
    messagebox.showerror("오류", "Pretendard 폰트를 찾을 수 없습니다.")
    sys.exit()

title = pygame.image.load(r"source\shingalism.png").convert_alpha()
title_rect = title.get_rect(center=(screen_width // 2, screen_height // 2))


def error_message(text):
    text_surface = font_48.render(text, True, (255, 255, 255))
    text_rect = text_surface.get_rect(center=(screen_width // 2, screen_height // 2))
    screen.blit(text_surface, text_rect)

texts = {
    "photo_information": "잠시후 사진 촬영이 시작됩니다",
    "num": [10, 9, 8, 7, 6, 5, 4, 3, 2, 1,"찰칵!"],
    "printing_information": "이용해주셔서 감사합니다! 출구 앞 카운터에서 사진을 수령해주세요"
}

def text_surface(text_address, index=None):
    if index is not None:
        re = font_48.render(str(texts[text_address][index]), True, (255, 255, 255))
    else:
        re = font_48.render(texts[text_address], True, (0, 0, 0))
    rect = re.get_rect(center=(screen_width // 2, screen_height // 2))
    return re, rect

program_running = True
next_button = Button(1600, 970, 200, 70, (200, 200, 200), "Next")
normal_button = Button(300,450,500,250,(200,200,200),"일반 프레임")
collab_button = Button(1100,450,500,250,(200,200,200),"선생님 프레임")

while program_running:
    running = True
    error = False
    page = 0
    page_is_available = False

    # 저장 경로
    file_name = datetime.now().strftime("%m_%Y_%H_%M_%S")
    save_dir = f"photo/{file_name}"
    os.makedirs(save_dir, exist_ok=True)

    captured_files = []        # 촬영된 6장 사진 경로
    selected_indices = []      # 선택된 사진 index (좌측 기준)
    selected_photos = []       # 선택된 Surface (우측에 띄우기)

    selected_theme = None
    current_frame_path = r"frame\black_frame_select.png"  # 기본 프레임
    selecting = "waiting"
    buttons_active = True
    in_collab_page = 0

    while running:
        try:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        print("\n[ 프로세스 종료됨 ]")
                        program_running = False
                        running = False
                    if event.key == pygame.K_SPACE or event.type == pygame.MOUSEBUTTONDOWN:
                        if page == 0:
                            page += 1
                            print(f"\n( {page}번째 페이지로 이동됨 ) \n")
                        elif page == 2:
                            pass
                        else:
                            print("페이지가 현재 작동중입니다.")
            if not error:
                # 페이지 0: 타이틀
                if page == 0:
                    screen.fill((235, 235, 235))
                    screen.blit(title, title_rect)
                    pygame.display.flip()

                # 페이지 1: 프레임 선택택
                elif page == 1:
                    if in_collab_page == 0:
                        page_is_available = True
                        screen.fill((235, 235, 235))
                        circle_positions_page = 3
                        mouse_pos = pygame.mouse.get_pos()
                        mouse_pressed = pygame.mouse.get_pressed()
                        if next_button.is_clicked(mouse_pos, mouse_pressed):
                            in_collab_page = 1
                        next_button.draw(screen)

                        #왼쪽 프레임
                        try:
                            left_frame = pygame.image.load(current_frame_path).convert_alpha()
                            left_frame = pygame.transform.smoothscale(left_frame, (300, 900))
                            screen.blit(left_frame, (150, 100))
                        except Exception as e:
                            current_frame_path = r"frame\black_frame_select.png"
                            left_frame = pygame.image.load(current_frame_path).convert_alpha()
                            left_frame = pygame.transform.smoothscale(left_frame, (300, 900))
                            screen.blit(left_frame, (150, 100))

                        #제목 텍스트
                        theme_text = font_48.render("Theme", True, (0, 0, 0))
                        screen.blit(theme_text, (670, 100))
                        shingal_text = font_48.render("Shingalism X 신갈고등학교", True, (0, 0, 0))
                        screen.blit(shingal_text, (670, 500))

                        #절대 경로 보정 함수
                        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
                        def abs_path(relative_path):
                            return os.path.join(BASE_DIR, relative_path)

                        #테마 버튼 정의
                        if 'circle_positions' not in globals() or circle_positions_page != 3:
                            circle_positions = []
                            circle_radius = 60
                            spacing = 180
                            #위쪽 3x2 테마 버튼
                            for row in range(2):
                                for col in range(5):
                                    x = 740 + col * spacing
                                    y = 230 + row * spacing
                                    circle_positions.append(("theme", len(circle_positions), (x, y)))
                            #아래쪽 3x2 콜라보 테마 버튼
                            for row in range(2):
                                for col in range(4):
                                    x = 740 + col * spacing
                                    y = 650 + row * spacing
                                    circle_positions.append(("collab", len(circle_positions), (x, y)))
                            #색상/이미지 설정
                            theme_styles = {
                                0: {"color": (0, 0, 0), "image": None},
                                1: {"color": (255, 255, 255), "image": None},
                                2: {"color": (194, 230, 255), "image": r"source\theme2.png"},
                                3: {"color": (0, 0, 0), "image": r"source\theme3.png"},
                                4: {"color": (0, 0, 0), "image": r"source\theme4.png"},
                                5: {"color": (0, 0, 0), "image": r"source\theme5.png"},
                                6: {"color": (0, 0, 0), "image": r"source\theme6.png"},
                                7: {"color": (0, 0, 0), "image": r"source\theme7.png"},
                                8: {"color": (0, 0, 0), "image": r"source\theme8.png"},
                                9: {"color": (0, 0, 0), "image": r"source\theme9.png"},
                                10: {"color": (0, 0, 0), "image": r"source\theme10.png"},
                                11: {"color": (0, 0, 0), "image": r"source\theme11.png"},
                                12: {"color": (0, 0, 0), "image": r"source\theme12.png"},
                                13: {"color": (0, 0, 0), "image": r"source\theme13.png"},
                                14: {"color": (0, 0, 0), "image": r"source\theme14.png"},
                                15: {"color": (0, 0, 0), "image": r"source\theme15.png"},
                                16: {"color": (0, 0, 0), "image": r"source\theme16.png"},
                                17: {"color": (0, 0, 0), "image": None}
                            }
                            #이미지 미리 로드 (없으면 색상으로 대체)
                            loaded_textures = {}
                            for idx, style in theme_styles.items():
                                img_path = style.get("image")
                                if img_path and os.path.exists(img_path):
                                    try:
                                        img = pygame.image.load(img_path).convert_alpha()
                                        img = pygame.transform.smoothscale(img,
                                                                           (circle_radius * 2, circle_radius * 2))
                                        loaded_textures[idx] = img
                                        print(f"[INFO] Texture loaded: {img_path}")
                                    except Exception as e:
                                        print(f"[WARN] Failed to load texture ({img_path}): {e}")
                                        loaded_textures[idx] = None
                                else:
                                    print(f"[WARN] Image not found: {img_path}")
                                    loaded_textures[idx] = None

                        #버튼 그리기
                        for t_type, idx, (x, y) in circle_positions:
                            color = theme_styles.get(idx, {"color": (180, 180, 180)})["color"]
                            texture = loaded_textures.get(idx)
                            #원형 마스크 Surface 생성
                            button_surface = pygame.Surface((circle_radius * 2, circle_radius * 2), pygame.SRCALPHA)
                            if texture:
                                #원형 마스크를 만들어 이미지 외곽을 둥글게 잘라냄
                                mask = pygame.Surface((circle_radius * 2, circle_radius * 2), pygame.SRCALPHA)
                                pygame.draw.circle(mask, (255, 255, 255), (circle_radius, circle_radius),
                                                   circle_radius)
                                texture_copy = texture.copy()
                                texture_copy.blit(mask, (0, 0), None, pygame.BLEND_RGBA_MIN)
                                button_surface.blit(texture_copy, (0, 0))
                            else:
                                pygame.draw.circle(button_surface, color, (circle_radius, circle_radius),
                                                   circle_radius)
                            #선택 강조 (빨간 테두리)
                            if selected_theme == idx:
                                pygame.draw.circle(button_surface, (255, 0, 0), (circle_radius, circle_radius),
                                                   circle_radius, 6)
                            screen.blit(button_surface, (x - circle_radius, y - circle_radius))

                        #클릭 판정 함수
                        def point_in_circle(px, py, cx, cy, radius, tol=4):
                            dx, dy = px - cx, py - cy
                            return dx * dx + dy * dy <= (radius + tol) ** 2

                        #이벤트 처리
                        for event in pygame.event.get():
                            if event.type == pygame.QUIT:
                                running = False
                            elif event.type == pygame.KEYDOWN:
                                if event.key == pygame.K_ESCAPE:
                                    running = False
                                elif event.key == pygame.K_SPACE:
                                    print(f"선택된 테마: {selected_theme}")
                                    page = 4
                            elif event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP) and getattr(event,
                                                                                                          'button',
                                                                                                          None) == 1:
                                px, py = event.pos
                                for t_type, idx, (x, y) in circle_positions:
                                    if point_in_circle(px, py, x, y, circle_radius):
                                        selected_theme = idx
                                        print(f"테마 {idx} 선택됨 (type={t_type})")
                                        # 프레임 경로 변경
                                        current_frame_path = abs_path(fr"frame\theme_{idx}_frame.png")
                                        frame_name = f"theme_{idx}_frame"
                                        break
                        pygame.display.flip()

                        #콜라보 사진 촬영
                        if in_collab_page == 1:
                            #촬영 관련 변수 초기화
                            photo_count = 0 
                            countdown_index = 0
                            frame_counter = 0 
                            #captured_files 초기화 시 기존 참조 유지
                            if 'captured_files' not in locals():
                                captured_files = []
                            else:
                                captured_files.clear()  #기존 리스트 유지하며 내부만 초기화

                            while photo_count < 8 and running:

                                def take_picture(frame):
                                    global photo_count, countdown_index
                                    sound = pygame.mixer.Sound(r"source\camera.mp3")
                                    sound.play()

                                    #3:2 비율 중앙 크롭
                                    height, width, _ = frame.shape
                                    target_ratio = 3 / 2

                                    if width / height > target_ratio:
                                        new_width = int(height * target_ratio)
                                        x1 = (width - new_width) // 2
                                        frame_cropped = frame[:, x1:x1 + new_width]
                                    else:
                                        new_height = int(width / target_ratio)
                                        y1 = (height - new_height) // 2
                                        frame_cropped = frame[y1:y1 + new_height, :]

                                    filepath = f"{save_dir}/{photo_count}.jpg"
                                    cv2.imwrite(filepath, frame_cropped)
                                    captured_files.append(filepath)
                                    print(f"사진 {photo_count} 저장됨: {filepath}")

                                    photo_count += 1
                                    countdown_index = 0

                                #이벤트 처리
                                for event in pygame.event.get():
                                    if event.type == pygame.QUIT:
                                        running = False
                                    elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                                        running = False
                                    elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                                        print("건너뛰기 감지 (SPACE)")
                                        take_picture(frame)
                                    elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                                        print("건너뛰기 감지 (Click)")
                                        take_picture(frame)

                                ret, frame = cap.read()
                                if not ret:
                                    break
                                frame = cv2.flip(frame, 1)

                                #화면 표시
                                frame_height, frame_width = frame.shape[:2]
                                scale_ratio = screen_height / frame_height
                                new_width = int(frame_width * scale_ratio)
                                resized_frame = cv2.resize(frame, (new_width, screen_height))
                                resized_frame = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)
                                frame_surface = pygame.surfarray.make_surface(resized_frame.swapaxes(0, 1))
                                screen.fill((235, 235, 235))
                                screen.blit(frame_surface,
                                            frame_surface.get_rect(center=(screen_width // 2, screen_height // 2)))

                                #카운트다운 로직
                                if frame_counter % 30 == 0:
                                    countdown_index += 1
                                if countdown_index < 11:
                                    msg, rect = text_surface("num", countdown_index)
                                    screen.blit(msg, rect)
                                elif countdown_index == 11:
                                    take_picture(frame)
                                frame_counter += 1

                                #안전한 프레임 오버레이
                                teacher_image_path = rf"source\frame_texture\{frame_name}\{photo_count}.png"
                                if photo_count >= 4:
                                    teacher_image_path = rf"source\frame_texture\{frame_name}\{photo_count-4}.png"
                                if os.path.exists(teacher_image_path):
                                    image = pygame.image.load(teacher_image_path).convert_alpha()
                                    image = pygame.transform.smoothscale(image, (1404, 1080))
                                    img_w, img_h = image.get_size()
                                    x = (screen_width - img_w) // 2
                                    y = (screen_height - img_h) // 2
                                    screen.blit(image, (x, y))

                                pygame.display.flip()
                            in_collab_page = 2
                            page = 2

                        # #콜라보 사진 선택 화면
                        # if in_collab_page == 2:
                        #     screen.fill((255, 255, 255))
                        #     page_is_available = True
                        #     mouse_pos = pygame.mouse.get_pos()
                        #     mouse_pressed = pygame.mouse.get_pressed()
                        #
                        #     # next 버튼
                        #     if next_button.is_clicked(mouse_pos, mouse_pressed):
                        #         if len(selected_photos) > 3:
                        #             page = 4
                        #             pass
                        #         else:
                        #             messagebox.showerror("오류", "선택된 사진이 부족합니다.")
                        #
                        #     next_button.draw(screen)
                        #
                        #     # 제목
                        #     try:
                        #         title_img = pygame.image.load(r"source\select photo.png").convert_alpha()
                        #         target_width, target_height = 1357, 144
                        #         title_img = pygame.transform.smoothscale(title_img, (target_width, target_height))
                        #         screen.blit(title_img, (50, 80))
                        #     except Exception:
                        #         pass
                        #
                        #     photos = []

                        #     for path in captured_files:
                        #         try:
                        #             img = pygame.image.load(path).convert_alpha()
                        #             img = pygame.transform.scale(img, (360, 260))
                        #             photos.append(img)
                        #         except Exception:
                        #             # 로드 실패한 경우 None 채워서 인덱스 정렬 유지
                        #             photos.append(None)
                        #
                        #     photo_rects = []
                        #     start_x, start_y = 30, 250
                        #     cols = 4  # 한 행에 4열이므로 cols=4
                        #     rows = 2
                        #     gap_x = 375
                        #     gap_y = 300
                        #
                        #     for row in range(rows):
                        #         for col in range(cols):
                        #             idx = row * cols + col
                        #             rect = pygame.Rect(start_x + col * gap_x, start_y + row * gap_y, 360, 260)
                        #             photo_rects.append((idx, rect))
                        #             if idx < len(photos) and photos[idx] is not None:
                        #                 screen.blit(photos[idx], rect)
                        #                 if idx in selected_indices:
                        #                     pygame.draw.rect(screen, (255, 0, 0), rect, 5)
                        #                     overlay = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
                        #                     overlay.fill((255, 0, 0, 60))
                        #                     screen.blit(overlay, rect)
                        #                 else:
                        #                     pygame.draw.rect(screen, (0, 0, 0), rect, 2)
                        #             else:
                        #                 # 빈 슬롯 표시
                        #                 pygame.draw.rect(screen, (230, 230, 230), rect)
                        #                 pygame.draw.rect(screen, (180, 180, 180), rect, 2)
                        #
                        #     selected_rects = []
                        #     right_x = 1570
                        #
                        #     for i in range(4):
                        #         rect = pygame.Rect(right_x, 132 + i * 199, 234, 176)
                        #         selected_rects.append(rect)
                        #         pygame.draw.rect(screen, (220, 220, 220), rect)
                        #         if i < len(selected_photos):
                        #             target_width, target_height = 234, 176
                        #             # selected_photos에 이미 Surface가 들어있다면 안전하게 스케일
                        #             try:
                        #                 selected_photo = pygame.transform.smoothscale(selected_photos[i],
                        #                                                               (target_width, target_height))
                        #                 screen.blit(selected_photo, rect)
                        #             except Exception:
                        #                 pass
                        #     try:
                        #         frame_img = pygame.image.load(fr"frame\select\{frame_name}.png").convert_alpha()
                        #         target_width, target_height = 300, 900
                        #         frame_img = pygame.transform.smoothscale(frame_img, (target_width, target_height))
                        #         screen.blit(frame_img, (1537, 50))
                        #     except Exception:
                        #         pass
                        #
                        #     #이벤트 처리
                        #     for event in pygame.event.get():
                        #         if event.type == pygame.QUIT:
                        #             running = False
                        #
                        #         if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        #             pos = event.pos
                        #             for idx, rect in photo_rects:
                        #                 if rect.collidepoint(pos):
                        #                     # 존재하지 않는 이미지 인덱스에 대한 안전 검사
                        #                     if idx >= len(photos) or photos[idx] is None:
                        #                         break
                        #                     if idx in selected_indices:
                        #                         pos_in_list = selected_indices.index(idx)
                        #                         selected_indices.remove(idx)
                        #                         if 0 <= pos_in_list < len(selected_photos):
                        #                             selected_photos.pop(pos_in_list)
                        #                         print(f"사진 {idx} 선택 취소됨")
                        #
                        #                     elif len(selected_indices) < 4:
                        #                         selected_indices.append(idx)
                        #                         # 우측에 보여줄 축소본 생성 (권장 크기 200x130 유지)
                        #                         try:
                        #                             selected_img = pygame.transform.scale(photos[idx], (200, 130))
                        #                         except Exception:
                        #                             # 만약 photos[idx]가 None이면 빈 Surface 삽입
                        #                             selected_img = pygame.Surface((200, 130))
                        #                             selected_img.fill((200, 200, 200))
                        #                         selected_photos.append(selected_img)
                        #
                        #                         select_dir = f"{save_dir}/selected"
                        #                         os.makedirs(select_dir, exist_ok=True)
                        #                         src = captured_files[idx]
                        #                         dst = os.path.join(select_dir, os.path.basename(src))
                        #                         # 중복 파일명 방지
                        #                         if os.path.exists(dst):
                        #                             base, ext = os.path.splitext(dst)
                        #                             counter = 1
                        #                             new_dst = f"{base}_{counter}{ext}"
                        #                             while os.path.exists(new_dst):
                        #                                 counter += 1
                        #                                 new_dst = f"{base}_{counter}{ext}"
                        #                             dst = new_dst
                        #                         try:
                        #                             shutil.copy(src, dst)
                        #                             print(f"선택된 사진 저장됨: {dst}")
                        #                         except Exception as e:
                        #                             print("파일 복사 실패:", e)
                        #                     else:
                        #                         # 이미 4장 선택되어 있음
                        #                         print("이미 4장이 선택되어 있습니다.")
                        #                     break
                        #
                        #     pygame.display.flip()
                #페이지 2: 사진 선택 페이지
                elif page == 2:
                    screen.fill((255, 255, 255))
                    page_is_available = True
                    mouse_pos = pygame.mouse.get_pos()
                    mouse_pressed = pygame.mouse.get_pressed()

                    if next_button.is_clicked(mouse_pos, mouse_pressed):
                        if len(selected_photos) > 3:
                            page = 4
                            print("\n( 4페이지로 이동됨. )\n")
                            pygame.time.delay(200)
                        else:
                            messagebox.showerror("오류", "선택된 사진이 부족합니다.")

                    next_button.draw(screen)

                    photos = []

                    for path in captured_files:
                        img = pygame.image.load(path)
                        img = pygame.transform.scale(img, (360, 260))
                        photos.append(img)

                    photo_rects = []
                    start_x, start_y = 30, 250
                    cols = 4
                    rows = 2
                    gap_x = 375
                    gap_y = 300

                    for row in range(rows):
                        for col in range(cols):
                            idx = row * cols + col
                            rect = pygame.Rect(start_x + col * gap_x, start_y + row * gap_y, 360, 260)
                            photo_rects.append((idx, rect))
                            if idx < len(photos) and photos[idx] is not None:
                                screen.blit(photos[idx], rect)
                                if idx in selected_indices:
                                    pygame.draw.rect(screen, (255, 0, 0), rect, 5)
                                    overlay = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
                                    overlay.fill((255, 0, 0, 60))
                                    screen.blit(overlay, rect)
                                else:
                                    pygame.draw.rect(screen, (0, 0, 0), rect, 2)
                            else:
                                #빈 슬롯 표시
                                pygame.draw.rect(screen, (230, 230, 230), rect)
                                pygame.draw.rect(screen, (180, 180, 180), rect, 2)

                    selected_rects = []
                    right_x = 1570

                    for i in range(4):
                        rect = pygame.Rect(right_x, 132 + i * 199, 234, 176)
                        selected_rects.append(rect)
                        pygame.draw.rect(screen, (220, 220, 220), rect)
                        if i < len(selected_photos):
                            target_width, target_height = 234, 176
                            selected_photo = pygame.transform.smoothscale(selected_photos[i], (target_width, target_height))
                            screen.blit(selected_photo, rect)
                    # _text_surface_ = font_36.render("다음으로 넘어가려면 SPACE키를 눌러주세요", True, (0, 0, 0))
                    # text_rect = _text_surface_.get_rect()
                    # text_rect.x, text_rect.y = 1200, 1000
                    # screen.blit(_text_surface_, text_rect)
                    
                    
                    #화면 요소들
                    title_img = pygame.image.load(r"source\select photo.png").convert_alpha()
                    target_width, target_height = 1357, 144
                    title_img = pygame.transform.smoothscale(title_img, (target_width, target_height))
                    screen.blit(title_img, (50, 80))
                    title_img = pygame.image.load(fr"frame\select\{frame_name}.png").convert_alpha()
                    target_width, target_height = 300, 900
                    title_img = pygame.transform.smoothscale(title_img, (target_width, target_height))
                    screen.blit(title_img, (1537, 50))

                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            running = False

                        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                            pos = event.pos
                            for idx, rect in photo_rects:
                                if rect.collidepoint(pos):
                                    if idx in selected_indices:
                                        pos_in_list = selected_indices.index(idx)
                                        selected_indices.remove(idx)
                                        selected_photos.pop(pos_in_list)
                                        print(f"사진 {idx} 선택 취소됨")

                                    elif len(selected_indices) < 4:
                                        selected_indices.append(idx)
                                        selected_img = pygame.transform.scale(photos[idx], (200, 130))
                                        selected_photos.append(selected_img)
                                        select_dir = f"{save_dir}/selected"
                                        os.makedirs(select_dir, exist_ok=True)
                                        src = captured_files[idx]
                                        dst = os.path.join(select_dir, os.path.basename(src))
                                        shutil.copy(src, dst)
                                        print(f"선택된 사진 저장됨: {dst}")
                    pygame.display.flip()
                #
                # elif page == 3:
                #     page_is_available = True
                #     screen.fill((235, 235, 235))
                #     circle_positions_page = 3
                #     #선택된 슬롯 이미지 표시
                #     selected_rects = []  # 슬롯 좌표 리스트 초기화
                #     slot_images = [rf"photo\{file_name}\{selected_indices[0]}.jpg",rf"photo\{file_name}\{selected_indices[1]}.jpg",rf"photo\{file_name}\{selected_indices[2]}.jpg",rf"photo\{file_name}\{selected_indices[3]}.jpg"]  # 예시 이미지 경로
                #     mouse_pos = pygame.mouse.get_pos()
                #     mouse_pressed = pygame.mouse.get_pressed()
                #
                #     if next_button.is_clicked(mouse_pos, mouse_pressed):
                #         if len(selected_photos) > 3:
                #             page = 4
                #             print("\n( 4페이지로 이동됨. )\n")
                #         else:
                #             messagebox.showerror("오류", "선택된 사진이 부족합니다.")
                #
                #     next_button.draw(screen)
                #     for i in range(4):
                #         rect = pygame.Rect(183, 182 + i * 199, 234, 176)
                #         selected_rects.append(rect)
                #         #슬롯에 들어갈 이미지 불러오기
                #         image_path = slot_images[i]  # i번째 슬롯 이미지
                #         if image_path and os.path.exists(image_path):
                #             try:
                #                 img = pygame.image.load(image_path).convert_alpha()
                #                 #슬롯 크기에 맞게 스케일 조정
                #                 img = pygame.transform.smoothscale(img, (rect.width, rect.height))
                #                 screen.blit(img, rect)
                #             except Exception as e:
                #                 print(f"[경고] {image_path} 불러오기 실패:", e)
                #                 pygame.draw.rect(screen, (220, 220, 220), rect)
                #         else:
                #             #이미지가 없으면 회색 기본 배경
                #             pygame.draw.rect(screen, (220, 220, 220), rect)
                #
                #     #왼쪽 프레임
                #     try:
                #         left_frame = pygame.image.load(current_frame_path).convert_alpha()
                #         left_frame = pygame.transform.smoothscale(left_frame, (300, 900))
                #         screen.blit(left_frame, (150, 100))
                #     except Exception as e:
                #         current_frame_path = r"frame\black_frame_select.png"
                #         left_frame = pygame.image.load(current_frame_path).convert_alpha()
                #         left_frame = pygame.transform.smoothscale(left_frame, (300, 900))
                #         screen.blit(left_frame, (150, 100))
                #
                #     #제목 텍스트
                #     theme_text = font_48.render("Theme", True, (0, 0, 0))
                #     screen.blit(theme_text, (670, 100))
                #     shingal_text = font_48.render("Shingalism X 신갈고등학교", True, (0, 0, 0))
                #     screen.blit(shingal_text, (670, 500))
                #     #절대 경로 보정 함수
                #     BASE_DIR = os.path.dirname(os.path.abspath(__file__))
                #     def abs_path(relative_path):
                #         return os.path.join(BASE_DIR, relative_path)
                #     #테마 버튼 정의
                #     if 'circle_positions' not in globals() or circle_positions_page != 3:
                #         circle_positions = []
                #         circle_radius = 60
                #         spacing = 180
                #         #위쪽 3x2 테마 버튼
                #         for row in range(2):
                #             for col in range(5):
                #                 x = 740 + col * spacing
                #                 y = 230 + row * spacing
                #                 circle_positions.append(("theme", len(circle_positions), (x, y)))
                #         #아래쪽 3x2 콜라보 테마 버튼
                #         for row in range(2):
                #             for col in range(4):
                #                 x = 740 + col * spacing
                #                 y = 650 + row * spacing
                #                 circle_positions.append(("collab", len(circle_positions), (x, y)))
                #         #색상,이미지 설정
                #         theme_styles = {
                #             0: {"color": (0, 0, 0), "image": None},
                #             1: {"color": (255, 255, 255), "image": None},
                #             2: {"color": (194, 230, 255), "image": r"source\theme2.png"},
                #             3: {"color": (0, 0, 0), "image": r"source\theme3.png"},
                #             4: {"color": (0, 0, 0), "image": r"source\theme4.png"},
                #             5: {"color": (0, 0, 0), "image": r"source\theme5.png"},
                #             6: {"color": (0, 0, 0), "image": r"source\theme6.png"},
                #             7: {"color": (0, 0, 0), "image": r"source\theme7.png"},
                #             8: {"color": (0, 0, 0), "image": r"source\theme8.png"},
                #             9: {"color": (0, 0, 0), "image": r"source\theme9.png"},
                #             10: {"color": (0, 0, 0), "image": r"source\theme10.png"},
                #             11: {"color": (0, 0, 0), "image": r"source\theme11.png"},
                #             12: {"color": (0, 0, 0), "image": r"source\theme12.png"},
                #             13: {"color": (0, 0, 0), "image": r"source\theme13.png"},
                #             14: {"color": (0, 0, 0), "image": r"source\theme14.png"},
                #             15: {"color": (0, 0, 0), "image": r"source\theme15.png"},
                #             16: {"color": (0, 0, 0), "image": r"source\theme16.png"},
                #             17: {"color": (0, 0, 0), "image": None}
                #         }
                #         #이미지 미리 로드 (없으면 색상으로 대체)
                #         loaded_textures = {}
                #         for idx, style in theme_styles.items():
                #             img_path = style.get("image")
                #             if img_path and os.path.exists(img_path):
                #                 try:
                #                     img = pygame.image.load(img_path).convert_alpha()
                #                     img = pygame.transform.smoothscale(img, (circle_radius * 2, circle_radius * 2))
                #                     loaded_textures[idx] = img
                #                     print(f"[INFO] Texture loaded: {img_path}")
                #                 except Exception as e:
                #                     print(f"[WARN] Failed to load texture ({img_path}): {e}")
                #                     loaded_textures[idx] = None
                #             else:
                #                 print(f"[WARN] Image not found: {img_path}")
                #                 loaded_textures[idx] = None
                #
                #     #버튼 그리기
                #     for t_type, idx, (x, y) in circle_positions:
                #         color = theme_styles.get(idx, {"color": (180, 180, 180)})["color"]
                #         texture = loaded_textures.get(idx)
                #         #원형 마스크 Surface 생성
                #         button_surface = pygame.Surface((circle_radius * 2, circle_radius * 2), pygame.SRCALPHA)
                #         if texture:
                #             #원형 마스크를 만들어 이미지 외곽을 둥글게 잘라냄
                #             mask = pygame.Surface((circle_radius * 2, circle_radius * 2), pygame.SRCALPHA)
                #             pygame.draw.circle(mask, (255, 255, 255), (circle_radius, circle_radius), circle_radius)
                #             texture_copy = texture.copy()
                #             texture_copy.blit(mask, (0, 0), None, pygame.BLEND_RGBA_MIN)
                #             button_surface.blit(texture_copy, (0, 0))
                #         else:
                #             pygame.draw.circle(button_surface, color, (circle_radius, circle_radius), circle_radius)
                #         #선택 강조 (빨간 테두리)
                #         if selected_theme == idx:
                #             pygame.draw.circle(button_surface, (255, 0, 0), (circle_radius, circle_radius), circle_radius, 6)
                #         screen.blit(button_surface, (x - circle_radius, y - circle_radius))
                #
                #     #클릭 판정 함수
                #     def point_in_circle(px, py, cx, cy, radius, tol=4):
                #         dx, dy = px - cx, py - cy
                #         return dx * dx + dy * dy <= (radius + tol) ** 2
                #
                #     #이벤트 처리
                #     for event in pygame.event.get():
                #         if event.type == pygame.QUIT:
                #             running = False
                #         elif event.type == pygame.KEYDOWN:
                #             if event.key == pygame.K_ESCAPE:
                #                 running = False
                #             elif event.key == pygame.K_SPACE:
                #                 print(f"선택된 테마: {selected_theme}")
                #                 page = 4
                #
                #         elif event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP) and getattr(event, 'button', None) == 1:
                #             px, py = event.pos
                #             for t_type, idx, (x, y) in circle_positions:
                #                 if point_in_circle(px, py, x, y, circle_radius):
                #                     selected_theme = idx
                #                     print(f"테마 {idx} 선택됨 (type={t_type})")
                #                     #프레임 경로 변경
                #                     if t_type == "theme":
                #                         current_frame_path = abs_path(fr"frame\theme_{idx}_frame.png")
                #                     else:
                #                         current_frame_path = abs_path(fr"frame\collab_{idx}_frame.png")
                #                     break
                #
                #     pygame.display.flip()

                elif page == 4:
                    page_is_available = True
                    screen.fill((235, 235, 235))
                    msg, rect = text_surface("printing_information")
                    screen.blit(msg, rect)
                    pygame.display.flip()
                    slot_images = [rf"photo\{file_name}\{selected_indices[0]}.jpg",rf"photo\{file_name}\{selected_indices[1]}.jpg",rf"photo\{file_name}\{selected_indices[2]}.jpg",rf"photo\{file_name}\{selected_indices[3]}.jpg"]  # 예시 이미지 경로

                    if selected_theme is None:
                        messagebox.showerror("오류", "테마가 선택되지 않았습니다.")
                        page = 3  #테마 선택 페이지로 돌아가기
                    else:
                        theme_frame_location = fr"frame\theme_{selected_theme}_frame.png"

                    make_film(slot_images[0],slot_images[1],slot_images[2],slot_images[3],theme_frame_location,file_name)
                    make_2(fr"photo\{file_name}.png")
                    try:
                        if on_google: upload_to_drive(fr"photo\{file_name}.png")
                        if printing: print_film(fr"photo\{file_name}.png")
                    except Exception as e:
                        print(f"""
문제가 발생하였습니다 :
{e}
                        """)


                    pygame.time.delay(2000)
                    running = False

        except Exception as e:
            screen.fill((0, 0, 0))
            print("예외 발생:", type(e), e)  #콘솔 출력
            messagebox.showerror("오류", f"{type(e).__name__}: {str(e)}")
            pygame.display.flip()
            error = True

pygame.quit()

cap.release()
