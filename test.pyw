import cv2

# 이미지 파일 경로를 직접 지정하세요.
# 예시: "C:/path/to/your/image.jpg"
image_path = r"D:/NACHE 24PS LOOKBOOK/WAVY RING SET SILVER.jpg"

# 이미지 파일 로드
image = cv2.imread(image_path)

if image is not None:
    # 이미지가 성공적으로 로드되었다면 화면에 표시
    cv2.imshow('Loaded Image', image)
    cv2.waitKey(0)  # 윈도우가 열린 상태를 유지하기 위해 키 입력 대기
    cv2.destroyAllWindows()
else:
    # 이미지 로드 실패 시 메시지 출력
    print(f"Failed to load image at path: {image_path}")
