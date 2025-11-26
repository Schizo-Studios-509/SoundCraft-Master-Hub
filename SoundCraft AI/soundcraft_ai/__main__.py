import pyto_ui as ui
from ai_helper import chat

class SoundCraftView(ui.View):
    def __init__(self):
        super().__init__()
        self.background_color = 'black'

        # Title
        self.title_label = ui.Label()
        self.title_label.text = "🎧 SoundCraft AI"
        self.title_label.alignment = ui.ALIGN_CENTER
        self.title_label.text_color = 'white'
        self.title_label.font = ('AvenirNext-Bold', 22)
        self.add_subview(self.title_label)

        # Input field
        self.prompt_field = ui.TextView()
        self.prompt_field.text = "Enter your prompt here..."
        self.prompt_field.font = ('Menlo', 14)
        self.prompt_field.text_color = 'white'
        self.prompt_field.background_color = '#222'
        self.add_subview(self.prompt_field)

        # Output box
        self.output_box = ui.TextView()
        self.output_box.editable = False
        self.output_box.font = ('Menlo', 13)
        self.output_box.text_color = 'white'
        self.output_box.background_color = '#111'
        self.add_subview(self.output_box)

        # Send button
        self.send_button = ui.Button(title='Send')
        self.send_button.background_color = '#333'
        self.send_button.tint_color = 'white'
        self.send_button.action = self.send_prompt
        self.add_subview(self.send_button)

    def did_appear(self):
        self.name = "SoundCraft AI"  # <-- moved here
        print("✅ SoundCraft AI UI loaded")

    def layout(self):
        """Dynamic layout"""
        w, h = self.width, self.height
        self.title_label.frame = (0, 20, w, 40)
        self.prompt_field.frame = (10, 70, w - 20, 150)
        self.output_box.frame = (10, 240, w - 20, h - 300)
        self.send_button.frame = (w / 2 - 50, h - 40, 100, 30)

    def send_prompt(self, sender):
        prompt = self.prompt_field.text.strip()
        if not prompt:
            self.output_box.text = "⚠️ Please enter a prompt."
            return

        self.output_box.text = "🎙️ Thinking..."
        response = chat(prompt)
        self.output_box.text = f"🪶 {response}"

def main():
    view = SoundCraftView()
    view.present('sheet')

if __name__ == "__main__":
    main()