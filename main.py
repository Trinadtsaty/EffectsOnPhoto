from back.back import AdjustmentLayer, Grid, Strip, StripAnimation, Noise
from PIL import Image


class CodecIMG:
    def __init__(self, input_path:str, output_path:str):
        self.image = Image.open(input_path).convert("RGBA")
        self.output_p = output_path

    def start(self):
        photoshop = AdjustmentLayer(self.image, self.output_p)
        photoshop.photoshop()
        self.image = photoshop.image
        photoshop.save()

    def grid(self):
        grid_pixel = Grid(self.image, self.output_p)
        grid_pixel.apply_grid_to_image()
        self.image = grid_pixel.image
        grid_pixel.save()

    def noise(self):
        noise = Noise(self.image, self.output_p)
        noise.apply_color_dodge_noise()
        self.image = noise.image
        noise.save()

    def strip(self, gradient = True):
        strip = Strip(self.image, self.output_p)
        strip.apply_strip_to_image(gradient = gradient)
        strip.save()

    def anymation(self, gradient = True, frame_duration = 100):
        anymation = StripAnimation(self.image, self.output_p, frame_duration)
        anymation.create_animation(gradient=gradient)
        anymation.save()

if __name__ == "__main__":
    photo = CodecIMG("start/input.png","end/output")
    photo.start()
    photo.grid()
    photo.noise()
    photo.strip(gradient = True)
    photo.anymation(gradient=False, frame_duration = 100)
