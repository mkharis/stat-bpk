mkdir -p ~/.streamlit/
echo "[general]
email = \"081332210xxx@gmail.com\"
" > ~/.streamlit/credentials.toml
echo "[server]
headless = true
port = $PORT
enableCORS = false
" > ~/.streamlit/config.toml
