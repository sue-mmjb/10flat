// Vercel function that receives one piece of one attached file for a case request and forwards it to the Google Apps
// Script, which joins the pieces in the request's private Drive folder. Each piece is at most 3 MB, so every request
// stays under Vercel's 4.5 MB body limit while a whole request can carry up to 25 MB of files.

const { str, body, forward } = require("./_shared");

const FILE_TYPE = /^(image\/(jpeg|png|webp|heic|heif|gif)|application\/pdf|application\/octet-stream)$/;
const CHUNK = 3000000;
const MAX_TOTAL = 25 * 1024 * 1024;

module.exports = async (req, res) => {
  if (req.method !== "POST") {
    res.setHeader("Allow", "POST");
    return res.status(405).json({ ok: false, error: "method_not_allowed" });
  }
  const b = body(req);
  if (!b) return res.status(400).json({ ok: false, error: "bad_request" });

  const piece = {
    type: "file_chunk",
    ref: str(b.ref, 20),
    token: str(b.token, 60),
    file: b.file,
    name: str(b.name, 120).replace(/[\\/:*?"<>|\u0000-\u001f]/g, "_"),
    mime: str(b.type, 60),
    chunk: b.chunk,
    chunks: b.chunks,
    data: typeof b.data === "string" ? b.data : "",
  };
  const size = Math.floor((piece.data.length * 3) / 4);
  const ok = /^10F-\d{6}-[A-Z0-9]{4}$/.test(piece.ref) && piece.token.length >= 20 && piece.name &&
    FILE_TYPE.test(piece.mime) && Number.isInteger(piece.file) && piece.file >= 0 && piece.file < 10 &&
    Number.isInteger(piece.chunks) && piece.chunks >= 1 && piece.chunks * CHUNK <= MAX_TOTAL + CHUNK &&
    Number.isInteger(piece.chunk) && piece.chunk >= 0 && piece.chunk < piece.chunks &&
    /^[A-Za-z0-9+/=]+$/.test(piece.data) && size > 0 && size <= CHUNK + 4;
  if (!ok) return res.status(422).json({ ok: false, error: "invalid" });

  const sent = await forward(piece, 25000);
  if (!sent.ok) {
    console.error("INTAKE FILE NOT DELIVERED", JSON.stringify({ ref: piece.ref, file: piece.file, chunk: piece.chunk, why: sent.why }));
    return res.status(sent.status).json({ ok: false, error: "forward_failed" });
  }
  return res.status(200).json({ ok: true });
};
