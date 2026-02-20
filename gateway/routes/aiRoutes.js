/**
 * AI routes: ask, explain, generate-docs (forward to Python).
 */

const express = require("express");
const router = express.Router();
const auth = require("../middleware/auth");
const aiController = require("../controllers/aiController");

router.post("/ask", auth, aiController.ask);
router.post("/explain", auth, aiController.explain);
router.post("/generate-docs", auth, aiController.generateDocs);

module.exports = router;
