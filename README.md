# Notionistics

Landing page for [notionistics.com](https://notionistics.com). Software solutions (Zapier/Notion/Typeform integrations, custom scripts) and Notion-styled avatars, by the Notionistics team.

Plain static HTML, no build step. Edit `index.html` and push; GitHub Pages redeploys automatically.

## Deploy (GitHub Pages + custom domain)

1. Repo **Settings â†’ Pages â†’ Build and deployment**: Source = *Deploy from a branch*, branch `main`, folder `/ (root)`.
2. The `CNAME` file already sets the custom domain to `notionistics.com`.
3. At your domain registrar, add these DNS records:

   | Type  | Name | Value                |
   |-------|------|----------------------|
   | A     | @    | 185.199.108.153      |
   | A     | @    | 185.199.109.153      |
   | A     | @    | 185.199.110.153      |
   | A     | @    | 185.199.111.153      |
   | CNAME | www  | frdspuzi.github.io   |

4. Once DNS propagates, tick **Enforce HTTPS** in Settings â†’ Pages.
