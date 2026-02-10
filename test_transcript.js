const { YoutubeTranscript } = require('youtube-transcript');

async function test() {
  const videoId = 'x7X9w_GIm1s';
  console.log(`Testing fetch for ${videoId}...`);
  try {
    const transcript = await YoutubeTranscript.fetchTranscript(videoId);
    console.log('Success!');
    console.log('Length:', transcript.length);
    console.log('First item:', transcript[0]);
  } catch (err) {
    console.error('FAILED:', err.name, err.message);
    if (err.cause) console.error('Cause:', err.cause);
  }
}

test();