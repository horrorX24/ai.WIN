<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Horror.ai | Access</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body { background-color: #0f0f12; color: #e2e2e6; font-family: sans-serif; }
        .hidden { display: none !important; }
        .fade-in { animation: fadeIn 0.3s ease-in; }
        @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
    </style>
</head>
<body class="min-h-screen flex items-center justify-center p-4">

    <div class="bg-[#16161a] border border-[#2d2d35] p-8 rounded-2xl w-full max-w-md shadow-2xl">
        <h1 class="text-3xl font-bold text-[#a87ffb] mb-6 text-center tracking-tighter">Horror.ai</h1>

        <div id="step-email" class="fade-in">
            <p class="text-sm text-gray-400 mb-4 text-center">Enter your Gmail to receive a 6-digit access code.</p>
            <input type="email" id="email-input" placeholder="name@gmail.com" 
                   class="w-full bg-[#0f0f12] border border-[#2d2d35] p-4 rounded-xl outline-none focus:border-[#a87ffb] mb-4 text-white text-center">
            <button onclick="requestOTP()" id="send-btn" class="w-full bg-white text-black font-bold py-3 rounded-xl hover:bg-gray-200 transition-all">
                Send Code to Gmail
            </button>
        </div>

        <div id="step-otp" class="hidden fade-in text-center">
            <p class="text-sm text-gray-400 mb-4">Enter the 6-digit code sent to your inbox.</p>
            <input type="text" id="otp-input" maxlength="6" placeholder="000000" 
                   class="w-full bg-[#0f0f12] border border-[#2d2d35] p-4 text-center text-3xl tracking-[0.5em] outline-none focus:border-[#a87ffb] mb-4 text-white font-mono">
            <button onclick="verifyOTP()" id="verify-btn" class="w-full bg-[#a87ffb] text-black font-bold py-3 rounded-xl hover:bg-[#9060eb]">
                Verify Identity
            </button>
            <button onclick="location.reload()" class="mt-4 text-xs text-gray-500 hover:text-white">Back to Email</button>
        </div>
    </div>

    <script>
        let savedEmail = "";

        async function requestOTP() {
            const email = document.getElementById('email-input').value;
            const btn = document.getElementById('send-btn');
            
            if(!email.includes('@')) return alert("Enter a valid Gmail.");

            btn.innerText = "SENDING...";
            btn.disabled = true;

            try {
                const response = await fetch('/api/otp/request', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ email: email })
                });

                if (response.ok) {
                    savedEmail = email;
                    document.getElementById('step-email').classList.add('hidden');
                    document.getElementById('step-otp').classList.remove('hidden');
                } else {
                    const data = await response.json();
                    alert("Error: " + data.error);
                    btn.innerText = "Send Code to Gmail";
                    btn.disabled = false;
                }
            } catch (err) {
                alert("Connection failed.");
                btn.disabled = false;
            }
        }

        async function verifyOTP() {
            const code = document.getElementById('otp-input').value;
            const response = await fetch('/api/otp/verify', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ email: savedEmail, code: code })
            });

            if (response.ok) {
                alert("Access Granted. Welcome to the void.");
                // Add redirect logic here
            } else {
                alert("Incorrect code. Check your Gmail.");
            }
        }
    </script>
</body>
</html>
