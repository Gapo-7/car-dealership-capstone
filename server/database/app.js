const express = require('express');
const cors = require('cors');
const fs = require('fs');
const path = require('path');
const mongoose = require('mongoose');
const Dealerships = require('./dealership');
const Reviews = require('./review');

const app = express();
app.use(cors());
app.use(express.json());
const port = Number(process.env.PORT || 3030);
const readData = (name, key) => JSON.parse(fs.readFileSync(path.join(__dirname, 'data', name), 'utf8'))[key];
const sampleDealers = readData('dealerships.json', 'dealerships');
const sampleReviews = readData('reviews.json', 'reviews');
let extraReviews = [];
let useMongo = false;

if (process.env.MONGODB_URL) {
  mongoose.connect(process.env.MONGODB_URL, { dbName: 'dealershipsDB', serverSelectionTimeoutMS: 3000 })
    .then(async () => {
      useMongo = true;
      if (await Dealerships.countDocuments() === 0) await Dealerships.insertMany(sampleDealers);
      if (await Reviews.countDocuments() === 0) await Reviews.insertMany(sampleReviews);
      console.log('MongoDB connected');
    })
    .catch((error) => console.warn('MongoDB unavailable; using bundled data:', error.message));
}

const dealers = async () => useMongo ? Dealerships.find().lean() : sampleDealers;
const reviews = async () => useMongo ? Reviews.find().lean() : [...sampleReviews, ...extraReviews];
const safely = (handler) => (req, res) => Promise.resolve(handler(req, res)).catch((error) => res.status(500).json({ error: error.message }));

app.get('/', (_req, res) => res.send('Welcome to the Dealership API'));
app.get('/fetchDealers', safely(async (_req, res) => res.json(await dealers())));
app.get('/fetchDealers/:state', safely(async (req, res) => {
  const all = await dealers();
  const state = req.params.state.toLowerCase();
  res.json(state === 'all' ? all : all.filter((item) => item.state.toLowerCase() === state || item.st?.toLowerCase() === state));
}));
app.get('/fetchDealer/:id', safely(async (req, res) => {
  const all = await dealers();
  res.json(all.filter((item) => item.id === Number(req.params.id)));
}));
app.get('/fetchReviews', safely(async (_req, res) => res.json(await reviews())));
app.get('/fetchReviews/dealer/:id', safely(async (req, res) => {
  const all = await reviews();
  res.json(all.filter((item) => item.dealership === Number(req.params.id)));
}));
app.post('/insert_review', safely(async (req, res) => {
  const input = req.body;
  const required = ['name', 'dealership', 'review', 'purchase_date', 'car_make', 'car_model', 'car_year'];
  if (required.some((field) => !input[field])) return res.status(400).json({ error: 'Missing review details' });
  const all = await reviews();
  const item = { ...input, id: Math.max(0, ...all.map((review) => review.id)) + 1,
    dealership: Number(input.dealership), car_year: Number(input.car_year), purchase: Boolean(input.purchase) };
  if (useMongo) await Reviews.create(item);
  else extraReviews.push(item);
  return res.status(201).json(item);
}));

app.listen(port, () => console.log(`Server is running on http://localhost:${port}`));
