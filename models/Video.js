const mongoose = require('mongoose');

// Define the schema for storing video learning content
const videoSchema = new mongoose.Schema({
  // The YouTube video URL
  youtubeUrl: {
    type: String,
    required: true,
  },
  // The video ID extracted from URL
  videoId: {
    type: String,
    required: true,
  },
  // Full transcript text from the video
  transcript: {
    type: String,
    required: true,
  },
  // AI-generated summary of the video
  summary: {
    type: String,
    required: true,
  },
  // Array of key learning points
  keyPoints: [{
    type: String,
  }],
  // Array of quiz questions with options and answers
  quizQuestions: [{
    question: String,
    options: [String],
    correctAnswer: String,
  }],
  // When this record was created
  createdAt: {
    type: Date,
    default: Date.now,
  },
});

// Create and export the model
module.exports = mongoose.model('Video', videoSchema);
