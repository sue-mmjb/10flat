# Case requests: Google Sheet and email

Every request sent from the website's "Start your case" page (`/start`) ends up in three places:

- **A row in a Google Sheet** (tab "Case requests"), with a Status column you can change as you work the case.
- **A private Google Drive folder** with any photos or documents the client attached (one sub-folder per request).
- **An email to 10flatlaw@gmail.com** (later contact@ the firm's domain) with the details and the files attached.

Setup takes about ten minutes. Do it while signed in to the Google account that should own the requests (for example 10flatlaw@gmail.com). Nobody outside that account can open the Sheet, the folder or the files unless you share them.

## The firm mailbox (can wait)

The script emails 10flatlaw@gmail.com for now. As of 3 Nov 2026 10flatlaw.com is not registered (the domain bought on
30 Oct is tenflatlaw.com, at GoDaddy), so contact@10flatlaw.com cannot receive mail yet. Once the firm's address works,
change `NOTIFY_TO` at the top of `Code.gs` and redeploy (see "If you change the script later"). The address has to receive mail. Either set up Google Workspace on the firm's domain, or add email forwarding for `contact@` at the domain registrar (most registrars, and Cloudflare Email Routing, do this for free) and forward it to 10flatlaw@gmail.com. To send the emails somewhere else, change `NOTIFY_TO` at the top of `Code.gs`.

## 1. Make the Sheet and paste the script

1. In Google Drive, create a new Google Sheet. Name it "10flat Law case requests".
2. In the Sheet, open **Extensions > Apps Script**.
3. Delete what is in the editor, paste the whole of `Code.gs` from this folder, and press **Save**.

## 2. Test it once

1. In the Apps Script editor, choose **testSetup** in the function menu at the top and press **Run**.
2. Google asks for permission (to edit the Sheet, create Drive folders and send email as you). Choose your account, then **Advanced > Go to project (unsafe) > Allow**. "Unsafe" only means Google has not reviewed this private script.
3. Check that a "Case requests" tab appeared with one test row, and that a test email reached 10flatlaw@gmail.com. Delete the test row.

## 3. Publish it as a web app

1. Press **Deploy > New deployment**. Click the gear next to "Select type" and choose **Web app**.
2. Description: "Website case requests". **Execute as: Me**. **Who has access: Anyone**.
3. Press **Deploy** and copy the **Web app URL** (it ends in `/exec`). Keep it private; it is the only key to the script.

"Anyone" is needed because the website's server posts to it without signing in. The URL is never shown on the website: only the website's server knows it.

## 4. Give the URL to the website

1. Open the project in Vercel: **Settings > Environment Variables**.
2. Add `INTAKE_WEBHOOK_URL` with the Web app URL as the value, for **Production** (and Preview if you want to test there).
3. Go to **Deployments**, open the latest one and press **Redeploy** so the new setting takes effect.

## 5. Try it

Send a test request from https://personal-injury-law-nine.vercel.app/start with a photo attached. Within a few seconds you should see the thank-you message on the page, a new row in the Sheet, the file in Drive and the email.

## If you change the script later

Edit `Code.gs` in the Apps Script editor, then **Deploy > Manage deployments > (pencil) > Version: New version > Deploy**. The URL stays the same, so Vercel needs no change.

## Limits worth knowing

- Up to 5 files and 3 MB in total per request (photos are shrunk on the client's phone before sending, so this is usually several photos).
- A free Gmail account can send about 100 emails a day from a script; Google Workspace allows more.
- The page tells the client their request was received only after the Sheet, the files and the email have all been saved.

## Optional: an alert when a request is not delivered

If the Sheet script is down or the URL is wrong, the client sees "we couldn't send your request", and the website writes
the request's reference, name and phone number to the Vercel function log. To be told straight away, add a second
environment variable in Vercel, `INTAKE_ALERT_URL`, set to any webhook that accepts JSON with a `text` field (a Slack or
Google Chat incoming webhook works). Then redeploy.

## Reference numbers

Every request gets a reference such as `10F-261103-K7QP`. The client sees it on the thank-you screen; it is in the
"Reference" column of the Sheet, the email subject and the Drive folder name. If you set the Sheet up before 3 Nov 2026,
paste the new `Code.gs` and redeploy (see "If you change the script later"), and add a "Reference" column after "Received".

## Visitor numbers

The pages load Vercel Web Analytics (no cookies). Turn it on once in Vercel: open the project, **Analytics**, **Enable**.
Until then the browser shows a harmless "not found" for `/_vercel/insights/script.js`.

## Update of 3 Nov 2026 (round 2 review)

The form now asks whether a government vehicle or property was involved, takes up to 10 files and 25 MB, and comes in
Spanish at /es/start. Files are sent in pieces after the request itself, and the script joins them in the request's
Drive folder. What this means for the Sheet:

- Paste the new `Code.gs` and redeploy (see "If you change the script later").
- If your "Case requests" tab already exists, insert a column called **Government involved** after **Texas county**
  (the script writes the columns in the order of `HEADERS` at the top of `Code.gs`).
- Each request now sends one email straight away (marked URGENT when a government may be involved, because notice
  deadlines can be as short as six months) and, when it has files, a second "Files received" email once they are all in.
- Optional: in the Apps Script editor add a daily time-driven trigger for `cleanUploads`, which forgets uploads that
  never finished.

