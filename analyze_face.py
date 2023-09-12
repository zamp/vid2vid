from deepface import DeepFace

def analyze_face_tokens(image):
	face_analysis = DeepFace.analyze(image)
	if len(face_analysis) > 0:
		emotion = face_analysis[0]["emotion"]

		#anger 	disgust 	fear 	happiness 	sadness 	surprise 	neutral
		return f"(angry, furious:{emotion['angry']/100.0:.1f}), (disgusted, disgust:{emotion['disgust']/100.0:.1f}), (fear, scared, terrified:{emotion['fear']/100.0:.1f}), (happy, smiling, smile:{emotion['happy']/100.0:0.1f}), (sad:{emotion['sad']/100.0:0.1f}), (surprised, shocked:{emotion['surprise']/100.0:0.1f})"

#print(analyze_face_tokens("video/039.png"))