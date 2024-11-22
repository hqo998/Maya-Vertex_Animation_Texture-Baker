from Qt import QtCore, QtGui, QtWidgets


def process_image(image_path):
    image = QtGui.QImage(image_path)

    if image.isNull():
        raise ValueError(f"Failed to load image from path: {image_path}")

    width = image.width()
    if width % 2 == .5:
        width += 1
    height = image.height()

    left_half = image.copy(0, 0, width // 2, height) #copy and save the left half to variable
    right_half = image.copy(width // 2, 0, width // 2, height) #copy and save right half to variable

    if image.format() == QtGui.QImage.Format_RGBX64:
        print("Doing Splits - 64bit")
        new_image = QtGui.QImage(width // 2, height * 2, QtGui.QImage.Format_RGBX64)
    else:
        new_image = QtGui.QImage(width // 2, height * 2, QtGui.QImage.Format_RGB888)
        print("Doing Splits - 24bit")

    painter = QtGui.QPainter(new_image)
    painter.drawImage(0, 0, left_half)
    painter.drawImage(0, height, right_half)
    painter.end()

    imagesaved = image_path.split(".")
    imagesaved = f"{imagesaved[0]}_Split.{imagesaved[1]}"
    new_image.save(imagesaved, quality=100)

    return new_image
