

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.graphics.texture import Texture
from kivy.clock import Clock

import cv2
from datetime import datetime
from geopy.geocoders import Nominatim
import requests
import os

class CameraApp(App):
    def build(self):
        # Camera preview
        self.img1 = Image(size_hint=(1, 0.8))
        
        # Labels
        self.clock_label = Label(size_hint=(1, 0.05), halign="center", valign="middle")
        self.label = Label(size_hint=(1, 0.1), halign="center", valign="middle")
        
        self.capture = cv2.VideoCapture(0)
        self.is_gray = False

        layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        layout.add_widget(self.clock_label)
        layout.add_widget(self.img1)
        layout.add_widget(self.label)

        # Buttons row
        btn_layout = BoxLayout(size_hint=(1, 0.05), spacing=10)
        self.capture_btn = Button(text="Capture Image", size_hint=(0.5, 1))
        self.capture_btn.bind(on_press=self.capture_image)

        self.filter_btn = Button(text="Toggle Grayscale", size_hint=(0.5, 1))
        self.filter_btn.bind(on_press=self.toggle_filter)

        btn_layout.add_widget(self.capture_btn)
        btn_layout.add_widget(self.filter_btn)

        layout.add_widget(btn_layout)

        Clock.schedule_interval(self.update, 1.0 / 30.0)
        Clock.schedule_interval(self.update_clock, 1.0)

        return layout

    def update(self, dt):
        ret, frame = self.capture.read()
        if ret:
            if self.is_gray:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)

            buf = cv2.flip(frame, 0).tobytes()
            texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
            texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
            self.img1.texture = texture
            self.current_frame = frame

    def update_clock(self, dt):
        self.clock_label.text = datetime.now().strftime("Current Time: %Y-%m-%d %H:%M:%S")

    def toggle_filter(self, *args):
        self.is_gray = not self.is_gray

    def get_ip_location(self):
        try:
            response = requests.get("https://ipinfo.io/json")
            data = response.json()
            loc = data['loc']  # e.g., "21.1498,79.0821"
            return loc
        except:
            return None

    def capture_image(self, *args):
        if not hasattr(self, 'current_frame'):
            self.label.text = "No frame to capture!"
            return

        frame = self.current_frame.copy()

        # Add watermark
        watermark = f"Sakshi Kadu {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        cv2.putText(frame, watermark, (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        # Save in folder
        if not os.path.exists("Captured_Images"):
            os.makedirs("Captured_Images")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"Captured_Images/captured_image_{timestamp}.png"
        cv2.imwrite(filename, frame)

        # Get approximate location from IP
        try:
            loc = self.get_ip_location()
            if loc:
                lat, lon = loc.split(',')
                geolocator = Nominatim(user_agent="camera_app")
                location = geolocator.reverse(f"{lat},{lon}")
                if location:
                    place = location.address
                    location_text = f"Lat: {lat}, Lon: {lon}\n{place}"
                else:
                    location_text = "Location not found."
            else:
                location_text = "Could not get IP location."
        except Exception as e:
            location_text = f"Error: {str(e)}"

        self.label.text = f"Saved: {filename}\n{location_text}"

    def on_stop(self):
        self.capture.release()

if __name__ == '__main__':
    CameraApp().run()
