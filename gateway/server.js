/**
 * DevMind Gateway - Server entry.
 */

const app = require("./app");
const connectDB = require("./config/db");

const PORT = process.env.NODE_PORT || 5000;

connectDB().then(() => {
  app.listen(PORT, () => {
    console.log(`DevMind Gateway running on http://localhost:${PORT}`);
  });
});
