# GitHub Pages Dashboard

This folder contains the static lululemon valuation dashboard for GitHub Pages.

Source files live under:

- `project/code/web/`

To refresh this folder after changing the valuation model or dashboard source, run:

```powershell
Copy-Item project\code\web\index.html docs\index.html -Force
Copy-Item project\code\web\styles.css docs\styles.css -Force
Copy-Item project\code\web\app.js docs\app.js -Force
Copy-Item project\code\web\dashboard-data.js docs\dashboard-data.js -Force
```

GitHub Pages settings:

- Source: deploy from a branch.
- Branch: `main`.
- Folder: `/docs`.

