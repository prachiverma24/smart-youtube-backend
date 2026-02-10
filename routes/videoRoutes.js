const express = require('express');
const router = express.Router();
const videoController = require('../controllers/videoController');

// POST /api/videos/process - Process a YouTube video URL
router.post('/process', videoController.processVideo);

// POST /api/videos/transcript - Process direct transcript input
router.post('/transcript', videoController.processTranscript);

// GET /api/videos - Get all processed videos
router.get('/', videoController.getAllVideos);

// GET /api/videos/:id - Get a specific video by ID
router.get('/:id', videoController.getVideoById);

module.exports = router;
