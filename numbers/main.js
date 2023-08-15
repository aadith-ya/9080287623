const express = require('express');
const axios = require('axios');

const app = express();
const port = 3000;

app.use(express.json());

app.get('/numbers', async (req, res) => {
  const urlParams = req.query.url;

  if (!urlParams || !Array.isArray(urlParams)) {
    return res.status(400).json({ error: 'Invalid URL parameters' });
  }

  const requests = urlParams.map(async (url) => {
    try {
      const response = await axios.get(url);
      return response.data.numbers;
    } catch (error) {
      console.error(`Error fetching ${url}: ${error.message}`);
      return [];
    }
  });

  try {
    const results = await Promise.all(requests);
    const mergedNumbers = results.reduce((merged, numbers) => merged.concat(numbers), []);
    const uniqueNumbers = Array.from(new Set(mergedNumbers));
    const sortedNumbers = uniqueNumbers.sort((a, b) => a - b);

    res.json({ numbers: sortedNumbers });
  } catch (error) {
    res.status(500).json({ error: 'Internal server error' });
  }
});

app.listen(port, () => {
  console.log(`Server started on port ${port}`);
});
