import os
import json
import secrets

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
import gradio as gr
import uvicorn

from webauthn import (
    generate_registration_options,
    verify_registration_response,
    generate_authentication_options,
    verify_authentication_response,
    options_to_json,
)
from webauthn.helpers import (
    bytes_to_base64url,
    base64url_to_bytes,
)
from webauthn.helpers.structs import (
    PublicKeyCredentialDescriptor,
    UserVerificationRequirement,
    AuthenticatorSelectionCriteria,
    AuthenticatorAttachment,
)

# Import the already-working Gradio application.
from app import demo


# =========================================================
# SERVER CONFIGURATION
# =========================================================

RP_ID = "localhost"
RP_NAME = "AI Virtual Fashion Studio"
ORIGIN = "http://localhost:8000"

SESSION_SECRET = os.environ.get(
    "FASHION_SESSION_SECRET",
    secrets.token_urlsafe(32),
)

app = FastAPI(
    title="AI Virtual Fashion Studio"
)

app.add_middleware(
    SessionMiddleware,
    secret_key=SESSION_SECRET,
    same_site="lax",
    https_only=False,  # localhost development
)


# =========================================================
# DEMO STORAGE
# =========================================================
# For a college/demo project only.
# Replace with SQLite/PostgreSQL for production.
#
# username -> {
#     "user_id": bytes,
#     "credential_id": bytes,
#     "credential_public_key": bytes,
#     "sign_count": int
# }
# =========================================================

USERS = {}
REGISTRATION_CHALLENGES = {}
AUTHENTICATION_CHALLENGES = {}


# =========================================================
# LOGIN PAGE
# =========================================================

LOGIN_HTML = r"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport"
          content="width=device-width, initial-scale=1.0">

    <title>AI Virtual Fashion Studio</title>

    <style>
        * {
            box-sizing: border-box;
        }

        body {
            margin: 0;
            min-height: 100vh;
            font-family: Inter, Arial, sans-serif;
            background:
                radial-gradient(circle at top left,
                    #f8e7ef 0,
                    transparent 35%),
                radial-gradient(circle at bottom right,
                    #e4ebff 0,
                    transparent 35%),
                #f7f7fb;
            color: #20202a;
        }

        .page {
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 30px;
        }

        .shell {
            width: min(1080px, 100%);
            display: grid;
            grid-template-columns: 1.05fr 0.95fr;
            background: rgba(255,255,255,0.94);
            border-radius: 28px;
            overflow: hidden;
            box-shadow: 0 24px 80px rgba(30,30,50,0.14);
        }

        .hero {
            padding: 55px;
            background: linear-gradient(
                145deg,
                #181824,
                #30243c
            );
            color: white;
            position: relative;
        }

        .brand {
            font-size: 15px;
            letter-spacing: 2px;
            text-transform: uppercase;
            opacity: 0.78;
            margin-bottom: 25px;
        }

        h1 {
            font-size: 48px;
            line-height: 1.02;
            margin: 0 0 20px;
        }

        .subtitle {
            font-size: 18px;
            line-height: 1.6;
            opacity: 0.84;
            max-width: 480px;
        }

        .feature-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 14px;
            margin-top: 38px;
        }

        .feature {
            padding: 20px;
            border: 1px solid rgba(255,255,255,0.14);
            border-radius: 18px;
            background: rgba(255,255,255,0.06);
        }

        .icon {
            font-size: 30px;
            margin-bottom: 10px;
        }

        .feature-title {
            font-weight: 700;
            margin-bottom: 6px;
        }

        .feature-text {
            font-size: 13px;
            line-height: 1.5;
            opacity: 0.72;
        }

        .login {
            padding: 55px 45px;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }

        .login h2 {
            font-size: 32px;
            margin: 0 0 8px;
        }

        .login p {
            color: #6b6b7a;
            line-height: 1.5;
        }

        label {
            display: block;
            font-weight: 600;
            margin: 22px 0 8px;
        }

        input {
            width: 100%;
            padding: 15px 16px;
            border: 1px solid #d9d9e2;
            border-radius: 12px;
            font-size: 16px;
            outline: none;
        }

        input:focus {
            border-color: #6e5ae6;
            box-shadow: 0 0 0 4px rgba(110,90,230,0.10);
        }

        button {
            width: 100%;
            padding: 15px 18px;
            border: 0;
            border-radius: 12px;
            font-size: 15px;
            font-weight: 700;
            cursor: pointer;
            margin-top: 14px;
        }

        .primary {
            background: #222131;
            color: white;
        }

        .secondary {
            background: #eeeef5;
            color: #282736;
        }

        .status {
            min-height: 48px;
            margin-top: 18px;
            padding: 13px;
            border-radius: 12px;
            background: #f4f4f8;
            color: #585866;
            font-size: 14px;
            line-height: 1.45;
        }

        .privacy {
            margin-top: 20px;
            font-size: 12px;
            color: #888895;
            line-height: 1.5;
        }

        @media (max-width: 850px) {
            .shell {
                grid-template-columns: 1fr;
            }

            .hero {
                padding: 38px 30px;
            }

            .login {
                padding: 38px 30px;
            }

            h1 {
                font-size: 38px;
            }
        }
    </style>
</head>

<body>

<div class="page">

    <div class="shell">

        <section class="hero">

            <div class="brand">
                AI Virtual Fashion Studio
            </div>

            <h1>
                Your Personal
                AI Fashion
                Concierge.
            </h1>

            <div class="subtitle">
                Experience virtual try-on, personalized fashion
                analysis, explainable style scores and accessory
                discovery in one intelligent platform.
            </div>

            <div class="feature-grid">

                <div class="feature">
                    <div class="icon">👤</div>
                    <div class="feature-title">
                        Personal Portrait
                    </div>
                    <div class="feature-text">
                        Upload your portrait and create a
                        personalized fashion profile.
                    </div>
                </div>

                <div class="feature">
                    <div class="icon">👗</div>
                    <div class="feature-title">
                        Garment Intelligence
                    </div>
                    <div class="feature-text">
                        Analyze garments and visualize
                        the virtual try-on.
                    </div>
                </div>

                <div class="feature">
                    <div class="icon">✨</div>
                    <div class="feature-title">
                        AI Styling
                    </div>
                    <div class="feature-text">
                        Get transparent style compatibility
                        scores and explanations.
                    </div>
                </div>

                <div class="feature">
                    <div class="icon">🛍️</div>
                    <div class="feature-title">
                        Accessory Discovery
                    </div>
                    <div class="feature-text">
                        Find complementary accessories and
                        shopping search links.
                    </div>
                </div>

            </div>

        </section>


        <section class="login">

            <h2>Welcome Back</h2>

            <p>
                Sign in using a passkey. Your device may use
                fingerprint, Face ID, Windows Hello or another
                supported authenticator.
            </p>

            <label for="username">
                Email or Username
            </label>

            <input
                id="username"
                autocomplete="username webauthn"
                placeholder="example@email.com"
            />

            <button
                class="primary"
                onclick="registerPasskey()"
            >
                🔐 Create Passkey
            </button>

            <button
                class="secondary"
                onclick="loginPasskey()"
            >
                👆 Sign in with Fingerprint / Face ID
            </button>

            <div
                id="status"
                class="status"
            >
                Ready.
            </div>

            <div class="privacy">
                Passkeys use public-key cryptography. The website
                stores the credential's public key rather than
                storing your fingerprint or Face ID image.
            </div>

        </section>

    </div>

</div>


<script>

function setStatus(message) {
    document.getElementById("status").textContent = message;
}


function base64urlToUint8Array(base64url) {

    const padding = "=".repeat(
        (4 - base64url.length % 4) % 4
    );

    const base64 = (
        base64url + padding
    )
    .replace(/-/g, "+")
    .replace(/_/g, "/");

    const binary = atob(base64);

    return Uint8Array.from(
        binary,
        char => char.charCodeAt(0)
    );
}


function uint8ArrayToBase64url(buffer) {

    const bytes = new Uint8Array(buffer);

    let binary = "";

    for (const byte of bytes) {
        binary += String.fromCharCode(byte);
    }

    return btoa(binary)
        .replace(/\+/g, "-")
        .replace(/\//g, "_")
        .replace(/=+$/g, "");
}


function prepareCreationOptions(options) {

    options.challenge =
        base64urlToUint8Array(options.challenge);

    options.user.id =
        base64urlToUint8Array(options.user.id);

    if (options.excludeCredentials) {

        options.excludeCredentials =
            options.excludeCredentials.map(item => ({
                ...item,
                id: base64urlToUint8Array(item.id)
            }));
    }

    return options;
}


function prepareRequestOptions(options) {

    options.challenge =
        base64urlToUint8Array(options.challenge);

    if (options.allowCredentials) {

        options.allowCredentials =
            options.allowCredentials.map(item => ({
                ...item,
                id: base64urlToUint8Array(item.id)
            }));
    }

    return options;
}


async function registerPasskey() {

    const username =
        document.getElementById("username").value.trim();

    if (!username) {
        setStatus("Enter your email or username first.");
        return;
    }

    if (!window.PublicKeyCredential) {
        setStatus(
            "This browser does not support WebAuthn/passkeys."
        );
        return;
    }

    try {

        setStatus(
            "Preparing passkey registration..."
        );

        const optionsResponse =
            await fetch("/register/options", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    username: username
                })
            });

        const options = await optionsResponse.json();

        if (!optionsResponse.ok) {
            throw new Error(
                options.detail || "Registration setup failed."
            );
        }

        const publicKey =
            prepareCreationOptions(options);

        setStatus(
            "Complete the fingerprint / Face ID / Windows Hello prompt..."
        );

        const credential =
            await navigator.credentials.create({
                publicKey: publicKey
            });

        const response = credential.response;

        const payload = {

            username: username,

            credential: {

                id: credential.id,

                rawId:
                    uint8ArrayToBase64url(
                        credential.rawId
                    ),

                type: credential.type,

                response: {

                    clientDataJSON:
                        uint8ArrayToBase64url(
                            response.clientDataJSON
                        ),

                    attestationObject:
                        uint8ArrayToBase64url(
                            response.attestationObject
                        )
                },

                authenticatorAttachment:
                    credential.authenticatorAttachment || null,

                clientExtensionResults:
                    credential.getClientExtensionResults
                        ? credential.getClientExtensionResults()
                        : {}
            }
        };

        const verifyResponse =
            await fetch("/register/verify", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(payload)
            });

        const result =
            await verifyResponse.json();

        if (!verifyResponse.ok) {
            throw new Error(
                result.detail || "Registration failed."
            );
        }

        setStatus(
            "Passkey created successfully. Opening your studio..."
        );

        window.location.href = "/studio/";

    } catch (error) {

        setStatus(
            "Registration error: " + error.message
        );
    }
}


async function loginPasskey() {

    const username =
        document.getElementById("username").value.trim();

    if (!username) {
        setStatus("Enter your email or username first.");
        return;
    }

    if (!window.PublicKeyCredential) {
        setStatus(
            "This browser does not support WebAuthn/passkeys."
        );
        return;
    }

    try {

        setStatus(
            "Preparing secure sign-in..."
        );

        const optionsResponse =
            await fetch("/login/options", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    username: username
                })
            });

        const options =
            await optionsResponse.json();

        if (!optionsResponse.ok) {
            throw new Error(
                options.detail || "Login setup failed."
            );
        }

        const publicKey =
            prepareRequestOptions(options);

        setStatus(
            "Complete the fingerprint / Face ID / Windows Hello prompt..."
        );

        const credential =
            await navigator.credentials.get({
                publicKey: publicKey
            });

        const response = credential.response;

        const payload = {

            username: username,

            credential: {

                id: credential.id,

                rawId:
                    uint8ArrayToBase64url(
                        credential.rawId
                    ),

                type: credential.type,

                response: {

                    authenticatorData:
                        uint8ArrayToBase64url(
                            response.authenticatorData
                        ),

                    clientDataJSON:
                        uint8ArrayToBase64url(
                            response.clientDataJSON
                        ),

                    signature:
                        uint8ArrayToBase64url(
                            response.signature
                        ),

                    userHandle:
                        response.userHandle
                            ? uint8ArrayToBase64url(
                                response.userHandle
                            )
                            : null
                },

                authenticatorAttachment:
                    credential.authenticatorAttachment || null,

                clientExtensionResults:
                    credential.getClientExtensionResults
                        ? credential.getClientExtensionResults()
                        : {}
            }
        };

        const verifyResponse =
            await fetch("/login/verify", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(payload)
            });

        const result =
            await verifyResponse.json();

        if (!verifyResponse.ok) {
            throw new Error(
                result.detail || "Login failed."
            );
        }

        setStatus(
            "Login successful. Opening your studio..."
        );

        window.location.href = "/studio/";

    } catch (error) {

        setStatus(
            "Login error: " + error.message
        );
    }
}

</script>

</body>
</html>
"""


# =========================================================
# FASTAPI ROUTES
# =========================================================

@app.get("/", response_class=HTMLResponse)
async def home():
    return HTMLResponse(LOGIN_HTML)


@app.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(
        url="/",
        status_code=303
    )


@app.post("/register/options")
async def registration_options(request: Request):

    body = await request.json()

    username = str(
        body.get("username", "")
    ).strip().lower()

    if not username:
        return JSONResponse(
            {"detail": "Username is required."},
            status_code=400
        )

    if username in USERS:
        return JSONResponse(
            {"detail": "User already exists. Use passkey sign-in."},
            status_code=409
        )

    user_id = secrets.token_bytes(32)

    options = generate_registration_options(
        rp_id=RP_ID,
        rp_name=RP_NAME,
        user_name=username,
        user_display_name=username,
        user_id=user_id,
        authenticator_selection=AuthenticatorSelectionCriteria(
            authenticator_attachment=AuthenticatorAttachment.PLATFORM,
            user_verification=UserVerificationRequirement.REQUIRED,
        ),
    )

    challenge = bytes(options.challenge)

    REGISTRATION_CHALLENGES[username] = {
        "challenge": challenge,
        "user_id": user_id,
    }

    return JSONResponse(
        json.loads(options_to_json(options))
    )


@app.post("/register/verify")
async def registration_verify(request: Request):

    body = await request.json()

    username = str(
        body.get("username", "")
    ).strip().lower()

    credential = body.get("credential")

    pending = REGISTRATION_CHALLENGES.get(username)

    if not pending:
        return JSONResponse(
            {"detail": "Registration session expired."},
            status_code=400
        )

    if not credential:
        return JSONResponse(
            {"detail": "Credential response is missing."},
            status_code=400
        )

    try:

        verification = verify_registration_response(
            credential=credential,
            expected_challenge=pending["challenge"],
            expected_rp_id=RP_ID,
            expected_origin=ORIGIN,
            require_user_verification=True,
        )

        USERS[username] = {
            "user_id": pending["user_id"],
            "credential_id": verification.credential_id,
            "credential_public_key": verification.credential_public_key,
            "sign_count": verification.sign_count,
        }

        del REGISTRATION_CHALLENGES[username]

        request.session["user"] = username

        return {
            "ok": True,
            "username": username,
        }

    except Exception as exc:

        return JSONResponse(
            {
                "detail":
                    f"Passkey registration verification failed: {exc}"
            },
            status_code=400
        )


@app.post("/login/options")
async def authentication_options(request: Request):

    body = await request.json()

    username = str(
        body.get("username", "")
    ).strip().lower()

    user = USERS.get(username)

    if not user:
        return JSONResponse(
            {
                "detail":
                    "No passkey is registered for this username."
            },
            status_code=404
        )

    options = generate_authentication_options(
        rp_id=RP_ID,
        allow_credentials=[
            PublicKeyCredentialDescriptor(
                id=user["credential_id"]
            )
        ],
        user_verification=UserVerificationRequirement.REQUIRED,
    )

    challenge = bytes(options.challenge)

    AUTHENTICATION_CHALLENGES[username] = challenge

    return JSONResponse(
        json.loads(options_to_json(options))
    )


@app.post("/login/verify")
async def authentication_verify(request: Request):

    body = await request.json()

    username = str(
        body.get("username", "")
    ).strip().lower()

    credential = body.get("credential")

    user = USERS.get(username)
    challenge = AUTHENTICATION_CHALLENGES.get(username)

    if not user or not challenge:
        return JSONResponse(
            {"detail": "Login session is invalid or expired."},
            status_code=400
        )

    if not credential:
        return JSONResponse(
            {"detail": "Authentication credential is missing."},
            status_code=400
        )

    try:

        verification = verify_authentication_response(
            credential=credential,
            expected_challenge=challenge,
            expected_rp_id=RP_ID,
            expected_origin=ORIGIN,
            credential_public_key=user["credential_public_key"],
            credential_current_sign_count=user["sign_count"],
            require_user_verification=True,
        )

        user["sign_count"] = verification.new_sign_count

        del AUTHENTICATION_CHALLENGES[username]

        request.session["user"] = username

        return {
            "ok": True,
            "username": username,
        }

    except Exception as exc:

        return JSONResponse(
            {
                "detail":
                    f"Passkey authentication failed: {exc}"
            },
            status_code=401
        )


# =========================================================
# PROTECT GRADIO STUDIO
# =========================================================

def get_current_user(request: Request):

    return request.session.get("user")


app = gr.mount_gradio_app(
    app,
    demo,
    path="/studio",
    auth_dependency=get_current_user,
)


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":

    print()
    print("=" * 70)
    print("AI VIRTUAL FASHION STUDIO")
    print("Passkey Login + AI Fashion Studio")
    print("=" * 70)
    print()
    print("Home/Login:")
    print("http://localhost:8000")
    print()
    print("Studio:")
    print("http://localhost:8000/studio/")
    print()
    print("Press CTRL+C to stop.")
    print("=" * 70)
    print()

    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
    )
