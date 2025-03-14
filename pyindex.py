from flask import Flask, render_template_string, request, jsonify, send_from_directory
import os
from datetime import datetime

app = Flask(__name__)

# Path to the text file where responses will be saved
response_file = os.path.join(os.path.dirname(__file__), 'res.txt')

# Path to the images folder (which is the same as the script's location)
IMAGES_FOLDER = os.path.dirname(__file__)

def save_response(name, action):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(response_file, 'a') as f:
        f.write(f"{timestamp} - Name: {name}, Action: {action}\n")

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Be My Super Awesome Valentine?</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.5.1/dist/confetti.browser.min.js"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Pacifico&family=Roboto:wght@400;700&display=swap');

        body {
            font-family: 'Roboto', sans-serif;
            cursor: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='40' height='48' viewport='0 0 100 100' style='fill:black;font-size:24px;'><text y='50%'>❤️</text></svg>") 16 0, auto;
        }

        .gradient-background {
            background: linear-gradient(45deg, #ff9a9e 0%, #fad0c4 99%, #fad0c4 100%);
            animation: gradient 15s ease infinite;
            background-size: 400% 400%;
        }

        @keyframes gradient {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }

        .bounce2 {
            animation: bounce2 2s ease infinite;
        }

        @keyframes bounce2 {
            0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
            40% { transform: translateY(-20px); }
            60% { transform: translateY(-10px); }
        }

        .floating {
            animation: floating 3s ease-in-out infinite;
        }

        @keyframes floating {
            0% { transform: translate(0, 0px); }
            50% { transform: translate(0, 15px); }
            100% { transform: translate(0, -0px); }
        }

        .spin {
            animation: spin 10s linear infinite;
        }

        @keyframes spin {
            100% { transform: rotate(360deg); }
        }

        .valentine-title {
            font-family: 'Pacifico', cursive;
            text-shadow: 3px 3px 0px rgba(0,0,0,0.1);
        }

        .btn-3d {
            position: relative;
            transition: all 0.3s ease;
            transform-style: preserve-3d;
            transform: translateZ(-25px);
        }

        .btn-3d:before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: inherit;
            transform: translateZ(-25px) rotateX(90deg);
            transform-origin: bottom;
        }

        .btn-3d:hover {
            transform: translateZ(-25px) rotateX(-90deg);
        }

        /* Added CSS to provide spacing around the buttons */
        #responseButtons {
            margin-top: 20px; /* Add space above the buttons */
            margin-bottom: 20px; /* Add space below the buttons */
            padding: 10px; /* Add some padding inside the container */
            justify-content: center; /* Ensure buttons are centered */
        }

        #yesButton, #noButton {
            min-width: 150px; /* Ensure buttons have a minimum width */
        }
    </style>
</head>
<body class="gradient-background min-h-screen flex items-center justify-center overflow-hidden">
    <div id="hearts" class="fixed inset-0 pointer-events-none"></div>

    <div id="namePrompt" class="flex flex-col items-center p-4 bg-white bg-opacity-80 rounded-xl shadow-2xl">
        <h2 class="valentine-title text-5xl font-bold text-pink-600 mb-6 floating">Enter your name, cutie pie! 💖</h2>
        <input type="text" id="nameInput" class="text-2xl p-2 rounded-md border-2 border-pink-400 mb-4 focus:outline-none focus:ring-2 focus:ring-pink-600 focus:border-transparent" placeholder="Your lovely name...">
        <button id="submitName" class="btn-3d text-[20px] font-medium bg-pink-500 text-white rounded-full px-8 py-3 hover:bg-pink-600 transition-all duration-300 transform hover:scale-110">
            Shall We Start Darling?❤️💞😘
        </button>
         <!-- Error Message Display -->
        <p id="nameError" class="text-red-500 text-sm italic hidden">Please enter your name!</p>
    </div>

    <div id="mainContent" class="flex flex-col items-center p-4 bg-white bg-opacity-80 rounded-xl shadow-2xl hidden">
        <img id="imageDisplay" src="{{ url_for('serve_image', filename='image1.gif') }}" alt="Cute kitten with flowers" class="rounded-lg h-[300px] w-[300px] object-cover shadow-lg floating" />
        <h2 id="valentineQuestion" class="valentine-title text-5xl font-bold text-pink-600 my-6 text-center floating"> <span id="username"></span>, Will you be my super awesome Valentine💞❣️? 🌟</h2>
        <div class="flex gap-6 pt-[20px] items-center relative" id="responseButtons">
            <button id="yesButton" class="btn-3d bounce2 text-[20px] font-medium bg-green-500 text-white rounded-full px-8 py-3 transition-all duration-300 hover:bg-green-600 transform hover:scale-110 focus:outline-none focus:ring-2 focus:ring-green-400 focus:ring-opacity-50">
                Absolutely! 😍
            </button>
            <button id="noButton" class="btn-3d text-[20px] font-medium bg-red-500 text-white rounded-full px-8 py-3 hover:bg-red-600 transition-all duration-300 transform hover:scale-110 focus:outline-none focus:ring-2 focus:ring-red-400 focus:ring-opacity-50">
                No way! 😅
            </button>
        </div>
    </div>

    <div id="wrongNamePage" class="flex flex-col items-center p-4 bg-white bg-opacity-80 rounded-xl shadow-2xl hidden">
        <h2 class="valentine-title text-5xl font-bold text-pink-600 mb-6 text-center floating">Oopsie! This super secret Valentine proposal is not for you! Soo Get Lost 🙄😒</h2>

    </div>

    <audio id="backgroundMusic" loop>
        <source src="{{ url_for('static', filename='background_music.mp3') }}" type="audio/mpeg">
    </audio>

    <script>
        const namePrompt = document.getElementById('namePrompt');
        const mainContent = document.getElementById('mainContent');
        const wrongNamePage = document.getElementById('wrongNamePage');
        const nameInput = document.getElementById('nameInput');
        const submitName = document.getElementById('submitName');
        const yesButton = document.getElementById('yesButton');
        const noButton = document.getElementById('noButton');
        const imageDisplay = document.getElementById('imageDisplay');
        const valentineQuestion = document.getElementById('valentineQuestion');
        const responseButtons = document.getElementById('responseButtons');
        const backgroundMusic = document.getElementById('backgroundMusic');
        const nameError = document.getElementById('nameError'); // Get the error message element... let noClickCount = 0;
        const usernameSpan = document.getElementById('username');
        let noClickCount = 0;
        const imagePaths = [
            "{{ url_for('serve_image', filename='image1.gif') }}",
            "{{ url_for('serve_image', filename='image2.gif') }}",
            "{{ url_for('serve_image', filename='image3.gif') }}",
            "{{ url_for('serve_image', filename='image4.gif') }}",
            "{{ url_for('serve_image', filename='image5.gif') }}",
            "{{ url_for('serve_image', filename='image6.gif') }}",
            "{{ url_for('serve_image', filename='image7.gif') }}"
        ];
        const noResponses = [
            "No! 🥺",
            "Are you suuuure? 🥺",
            "Pretty pleaseeee! 😢😟",
            "Don't break my heart! 💔",
            "Please Dont make me loney😭🥺 ",
            "No,I'm gonna cry... 😭😭😭🌹"
        ];

        function createHeart() {
            const heart = document.createElement('div');
            heart.classList.add('heart');
            heart.style.left = Math.random() * 100 + "vw";
            heart.style.animationDuration = Math.random() * 2 + 3 + "s";
            heart.innerText = '❤️';
            heart.style.fontSize = Math.random() * 20 + 10 + "px";
            heart.style.position = 'fixed';
            heart.style.top = '-5vh';
            heart.style.animation = `fall ${Math.random() * 2 + 3}s linear`;
            document.getElementById('hearts').appendChild(heart);

            setTimeout(() => {
                heart.remove();
            }, 5000);
        }

        setInterval(createHeart, 300);

        function smoothScale(clickCount, smoothness = 0.5) {
            const scale = 1 + (clickCount * smoothness) / (1 + Math.exp(-clickCount));
            return scale.toFixed(2);
        }

        function moveCryButton() {
            const container = document.body.getBoundingClientRect();
            const imageRect = imageDisplay.getBoundingClientRect(); // Get image position
            const buttonRect = noButton.getBoundingClientRect();

            // Calculate a safe zone around the image to avoid overlap
            const safeMargin = 50; // Adjust this value as needed

            let newX = Math.random() * (container.width - buttonRect.width);
            let newY = Math.random() * (container.height - buttonRect.height);

            // Keep trying new positions until it's outside the image's safe zone
            while (
                newX > imageRect.left - buttonRect.width - safeMargin &&
                newX < imageRect.right + safeMargin &&
                newY > imageRect.top - buttonRect.height - safeMargin &&
                newY < imageRect.bottom + safeMargin
            ) {
                newX = Math.random() * (container.width - buttonRect.width);
                newY = Math.random() * (container.height - buttonRect.height);
            }

            noButton.style.position = 'fixed';
            noButton.style.left = `${newX}px`;
            noButton.style.top = `${newY}px`;
            noButton.style.transition = 'all 0.5s ease';
        }

       submitName.addEventListener('click', function() {
            const name = nameInput.value.trim().toLowerCase();

            if (name === "") {
                // Show error message
                nameError.classList.remove('hidden');
                return; // Stop further execution
            } else {
                // Hide error message if it was previously shown
                nameError.classList.add('hidden');
            }

            fetch('/check-name', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({name: name}),
            })
            .then(response => response.json())
            .then(data => {
                if (data.valid) {
                    namePrompt.classList.add('hidden');
                    mainContent.classList.remove('hidden');
                    usernameSpan.textContent = nameInput.value; //set username
                    backgroundMusic.play();
                } else {
                    namePrompt.classList.add('hidden');
                    wrongNamePage.classList.remove('hidden');
                }
            });
        });


        function sendAnswer(answer) {
            fetch('/save-answer', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({name: nameInput.value, answer: answer}),
            });
        }

        yesButton.addEventListener('click', function() {
            sendAnswer('Yes');
            imageDisplay.src = '{{ url_for('serve_image', filename='image7.gif') }}';
            valentineQuestion.textContent = "Yayyy! Love you Too💞❤️💏 You've made me the happiest person ever! 💖🎉";
            responseButtons.style.display = 'none';
            confetti({
                particleCount: 100,
                spread: 70,
                origin: { y: 0.6 }
            });
            setInterval(() => {
                confetti({
                    particleCount: 50,
                    spread: 70,
                    origin: { y: 0.6 }
                });
            }, 3000);
        });

        noButton.addEventListener('click', function() {
            sendAnswer('No');
            noClickCount++;
            if (noClickCount <= 5) {
                imageDisplay.src = imagePaths[noClickCount];
                noButton.textContent = noResponses[noClickCount];
                yesButton.style.transform = `scale(${smoothScale(noClickCount)})`;
                moveCryButton();
            }
            if (noClickCount === 5) {
                noButton.addEventListener('mouseover', moveCryButton);
            }
        });

        // Annoyingly playful cursor-chasing heart
        const chasingHeart = document.createElement('div');
        chasingHeart.innerText = '';
        chasingHeart.style.position = 'fixed';
        chasingHeart.style.pointerEvents = 'none';
        chasingHeart.style.zIndex = '9999';
        document.body.appendChild(chasingHeart);

        document.addEventListener('mousemove', (e) => {
            const x = e.clientX;
            const y = e.clientY;
            const xOffset = Math.sin(Date.now() / 300) * 20;
            const yOffset = Math.cos(Date.now() / 300) * 20;
            chasingHeart.style.left = `${x + xOffset}px`;
            chasingHeart.style.top = `${y + yOffset}px`;
        });
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/images/<path:filename>')
def serve_image(filename):
    return send_from_directory(IMAGES_FOLDER, filename)

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

@app.route('/check-name', methods=['POST'])
def check_name():
    data = request.json
    name = data['name'].lower()
    valid_names = ['lassya', 'lassya m kotian', 'ssumathii', 'anitha', 'lassu', 'anitha s', 'anitha s k']
    is_valid = name in valid_names
    save_response(name, "Login attempt")
    return jsonify({'valid': is_valid})

@app.route('/save-answer', methods=['POST'])
def save_answer():
    data = request.json
    name = data['name']
    answer = data['answer']
    save_response(name, f"Answered: {answer}")
    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(debug=True)
