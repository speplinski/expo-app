import cv2


def overlay_images(base_img, overlay_img):
    result = base_img.copy()

    b, g, r, a = cv2.split(overlay_img)

    overlay_color = cv2.merge((b, g, r))

    alpha = a.astype(float) / 255.0
    alpha_weights = cv2.merge([alpha, alpha, alpha])

    result = cv2.convertScaleAbs(base_img * (1.0 - alpha_weights) + overlay_color * alpha_weights)

    return result