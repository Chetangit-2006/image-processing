import cv2
import numpy as np
import time

INPUT_IMAGE = "staircase_450x450.png"
OUTPUT_IMAGE = "FAST_Final_Output.jpg"




# Lower value = more corners
FAST_THRESHOLD = 5

# FAST-9 detects more corners
FAST_TYPE = cv2.FAST_FEATURE_DETECTOR_TYPE_9_16




# Distance between red dots
# Increase this for more gap
MIN_DISTANCE = 8

# Radius of red dot
DOT_RADIUS = 2

# Red intensity
# (B, G, R)
DOT_COLOR = (0, 0, 180)


print("==============================================")
print("       FAST CORNER DETECTION PROJECT")
print("==============================================")

print("\nLoading image...")

original = cv2.imread(INPUT_IMAGE)

if original is None:

    print("ERROR: Image not found!")
    print("Make sure test_image.png is in the same folder.")

    exit()

print("Image loaded successfully!")


gray = cv2.cvtColor(
    original,
    cv2.COLOR_BGR2GRAY
)



print("Removing noise...")

denoised = cv2.fastNlMeansDenoising(
    gray,
    None,
    h=4,
    templateWindowSize=7,
    searchWindowSize=21
)



print("Enhancing clarity...")

clahe = cv2.createCLAHE(
    clipLimit=1.2,
    tileGridSize=(8, 8)
)

enhanced = clahe.apply(
    denoised
)


print("Sharpening image...")

blurred = cv2.GaussianBlur(
    enhanced,
    (0, 0),
    1.2
)

sharpened = cv2.addWeighted(
    enhanced,
    1.7,
    blurred,
    -0.7,
    0
)

sharpened = np.clip(
    sharpened,
    0,
    255
).astype(np.uint8)



print("Creating FAST detector...")

fast = cv2.FastFeatureDetector_create(
    threshold=FAST_THRESHOLD,

    # Detect all possible candidates
    nonmaxSuppression=False,

    type=FAST_TYPE
)


print("Detecting FAST corners...")

start_time = time.perf_counter()

keypoints = fast.detect(
    sharpened,
    None
)

detection_time = (
    time.perf_counter() - start_time
)

print(
    "Raw FAST corners:",
    len(keypoints)
)


candidates = []

for kp in keypoints:

    x = int(round(kp.pt[0]))
    y = int(round(kp.pt[1]))

    if x < 4:
        continue

    if y < 4:
        continue

    if x >= sharpened.shape[1] - 4:
        continue

    if y >= sharpened.shape[0] - 4:
        continue

    candidates.append(
        (x, y, kp.response)
    )


def corner_strength(image, x, y):

    center = int(
        image[y, x]
    )

    score = 0

    for dy in range(-2, 3):

        for dx in range(-2, 3):

            if dx == 0 and dy == 0:
                continue

            value = int(
                image[y + dy, x + dx]
            )

            score += abs(
                value - center
            )

    return score



scored = []

for x, y, response in candidates:

    strength = corner_strength(
        sharpened,
        x,
        y
    )

    score = (
        float(response) * 0.5 +
        float(strength) * 0.5
    )

    scored.append(
        (score, x, y)
    )


scored.sort(
    key=lambda p: (
        -p[0],
        p[2],
        p[1]
    )
)

print("Applying controlled corner spacing...")

selected = []

min_distance_squared = (
    MIN_DISTANCE * MIN_DISTANCE
)


for score, x, y in scored:

    keep = True

    # Check distance from previously selected points
    for sx, sy in selected:

        dx = x - sx
        dy = y - sy

        distance_squared = (
            dx * dx +
            dy * dy
        )

        if distance_squared < min_distance_squared:

            keep = False
            break

    if keep:

        selected.append(
            (x, y)
        )


output = original.copy()



print("Drawing corner marks...")

for x, y in selected:

    cv2.circle(
        output,
        (x, y),
        DOT_RADIUS,
        DOT_COLOR,
        -1,
        cv2.LINE_AA
    )


cv2.imwrite(
    OUTPUT_IMAGE,
    output,
    [
        cv2.IMWRITE_JPEG_QUALITY,
        100
    ]
)


print("\n==============================================")
print("              FINAL RESULTS")
print("==============================================")

print(
    "FAST threshold:",
    FAST_THRESHOLD
)

print(
    "FAST type: FAST-9"
)

print(
    "Raw corners:",
    len(candidates)
)

print(
    "Final spaced corners:",
    len(selected)
)

print(
    "Minimum dot gap:",
    MIN_DISTANCE,
    "pixels"
)

print(
    "Detection time:",
    round(
        detection_time,
        6
    ),
    "seconds"
)

print(
    "Output:",
    OUTPUT_IMAGE
)

print("==============================================")


cv2.imshow(
    "FAST - Spaced Red Corner Points",
    output
)

print("\nPress any key to close.")

cv2.waitKey(0)

cv2.destroyAllWindows()

print("\nProgram completed successfully!")