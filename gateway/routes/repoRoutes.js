/**
 * Repo routes: ingest (forward to Python).
 */

const express = require("express");
const router = express.Router();
const auth = require("../middleware/auth");
const repoController = require("../controllers/repoController");

router.post("/ingest", auth, repoController.ingest);

module.exports = router;
