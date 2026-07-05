# Dynamic Luck — Static Site Mockup

This is a single self-contained static HTML file (`index.html`) with all CSS and JavaScript inline, no build step, no dependencies. It includes every page: Home, Login, Signup, Game, Payment, Profile, and Leaderboard, all with dummy demo data.

## How to upload to GitHub

1. Create a new repository on GitHub (e.g. `dynamic-luck-site`).
2. On your computer, unzip this file and you'll have a folder with `index.html` and this `README.md`.
3. Upload both files to the repo:
   - Easiest: on the GitHub repo page, click **Add file → Upload files**, drag in `index.html` (and this README), then commit.
   - Or via git:
     ```
     git init
     git add .
     git commit -m "Initial site"
     git branch -M main
     git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
     git push -u origin main
     ```

## How to host it for free (GitHub Pages)

1. In your GitHub repo, go to **Settings → Pages**.
2. Under "Build and deployment", set **Source** to `Deploy from a branch`.
3. Set **Branch** to `main` and folder to `/ (root)`, then **Save**.
4. Wait a minute — GitHub will give you a live URL like `https://YOUR_USERNAME.github.io/YOUR_REPO/`.

## How to host it on your own website

Just upload `index.html` to your web host (via FTP, cPanel file manager, Netlify drag-and-drop, Vercel, etc.) as the root file of your site or a subfolder. No server, database, or build process is required — it's plain HTML/CSS/JS.

## Notes

- All data (wallet balance, transactions, leaderboard, winners) is hardcoded demo data for visual/UX purposes only — nothing is connected to a real backend.
- Login/Signup, Payment, and the Game page are wired with simple in-page JavaScript so you can click through the full experience (claim a number, top up wallet, etc.), but nothing persists after a page refresh.
