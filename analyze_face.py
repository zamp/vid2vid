from deepface import DeepFace
import util
from PIL import Image
import numpy as np

def analyze_face_tokens(image):
	img = Image.open(image)
	face_analysis = DeepFace.analyze(np.asarray(img), actions=("emotion"))
	img.close()

	if len(face_analysis) > 0:
		emotion = face_analysis[0]["emotion"]

		s = f"(angry, furious:{emotion['angry']/100.0:.1f}), "
		s += f"(disgusted, disgust:{emotion['disgust']/100.0:.1f}), "
		s += f"(fear, scared, terrified:{emotion['fear']/100.0:.1f}), "
		s += f"(happy, smiling, smile:{emotion['happy']/100.0:0.1f}), "
		s += f"(sad:{emotion['sad']/100.0:0.1f}), "
		s += f"(surprised, shocked:{emotion['surprise']/100.0:0.1f}), "
		s += f"(neutral expression:{emotion['neutral']/100.0:0.1f})"

		print(s)

		return s
	
def analyze_face_tokens_from_files(dir):
	files = util.get_png_files(dir)
	tokens = {}
	for file in files:
		frame = util.get_frame_int(file)
		print(file)
		tokens[frame] = analyze_face_tokens(dir+file)
	return tokens

#print(analyze_face_tokens("video/039.png"))