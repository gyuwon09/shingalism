import os
from PIL import Image, ImageWin
import subprocess


def make_film(path1: str, path2: str, path3: str, path4: str, frame: str, index_num: int):
    #캔버스 사이즈
    canvas_width = 800
    canvas_height = 2400
    canvas = Image.new("RGBA", (canvas_width, canvas_height), (255, 255, 255, 255))

    path_list = [path1, path2, path3, path4]
    y_setting = [218, 750, 1282, 1814]  #Y좌표 기준

    for idx, path in enumerate(path_list):
        #이미지 열기 및 리사이즈
        img = Image.open(path).convert("RGBA")
        img = img.resize((624, 468), Image.LANCZOS)

        #붙일 위치 계산
        x = (canvas_width - 624) // 2
        y = y_setting[idx]
        
        canvas.paste(img, (x, y), mask=img)

    #프레임 이미지 붙이기
    frame_img = Image.open(frame).convert("RGBA")
    frame_img = frame_img.resize((canvas_width, canvas_height), Image.LANCZOS)
    canvas.paste(frame_img, (0, 0), mask=frame_img)

    #저장
    output_dir = "photo"
    os.makedirs(output_dir, exist_ok=True)

    output_file = os.path.join(output_dir, f"{index_num}.png")
    canvas.save(output_file, format="PNG")

    print(f"'{output_file}' 파일이 생성되었습니다.")


def print_film(path):
    command = rf'powershell -NoProfile -ExecutionPolicy Bypass -File "print_command.ps1" -ImagePath "{path}" -PrinterName "Samsung SL-T1670W Series" -PaperSizePreset "4x6"'
    result = subprocess.run(command, shell=True)
    print(f"출력 명령 하달됨. {result}")

def make_2(img):
    """
    두 개의 400x1200 이미지를 좌우로 합쳐 800x1200 이미지를 만드는 함수.

    Parameters:
        img_path1 (str): 첫 번째 이미지 경로 (왼쪽에 위치)
        img_path2 (str): 두 번째 이미지 경로 (오른쪽에 위치)
        output_path (str): 합친 결과를 저장할 경로
    """

    output_path = img
    #이미지 열기
    img1 = Image.open(img)
    img2 = Image.open(img)

    #크기 확인 및 강제 리사이즈 (필요할 경우)
    img1 = img1.resize((400, 1200))
    img2 = img2.resize((400, 1200))

    #새 이미지 생성 (가로 800, 세로 1200)
    merged_img = Image.new("RGB", (800, 1200))

    #왼쪽에 첫 번째, 오른쪽에 두 번째 이미지 붙이기
    merged_img.paste(img1, (0, 0))
    merged_img.paste(img2, (400, 0))

    #저장
    merged_img.save(output_path)
    print(f"합쳐진 이미지가 저장되었습니다: {output_path}")

# 예시 실행
# merge_images_horizontally("left.jpg", "right.jpg", "merged.jpg")
# make_film(r"C:\gyuwon\personal\personal\Python\shingal_4cut\photo\chanhee\0.jpg",
#           r"C:\gyuwon\personal\personal\Python\shingal_4cut\photo\chanhee\1.jpg",
#           r"C:\gyuwon\personal\personal\Python\shingal_4cut\photo\chanhee\2.jpg",
#           r"C:\gyuwon\personal\personal\Python\shingal_4cut\photo\chanhee\3.jpg",
#           r"C:\gyuwon\personal\personal\Python\shingal_4cut\frame\theme_3_frame.png",
#           13)


# make_2(r"C:\gyuwon\personal\personal\Python\shingal_4cut\photo\0.png")

