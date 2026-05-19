// queries/part3_aggregations.js
// Запуск: mongosh "ВАШ_URI" --file queries/part3_aggregations.js

const dbName = "spotify";
const currentDb = db.getSiblingDB(dbName);
console.log(`=== ВИКОНАННЯ ЧАСТИНИ 3: АНАЛІТИКА (База: ${dbName}) ===\n`);

// =========================================================================
// Завдання 1. Топ-10 виконавців за середньою популярністю
// =========================================================================
console.log("--- Завдання 1: Топ-10 виконавців за середньою популярністю ---");

const topArtistsPipeline = [
    { $unwind: "$artists" },
    {
        $group: {
            _id: "$artists",
            total_tracks: { $sum: 1 },
            avg_popularity: { $avg: "$popularity" }
        }
    },
    { $match: { total_tracks: { $gte: 5 } } },
    { $sort: { avg_popularity: -1 } },
    { $limit: 10 },
    {
        $project: {
            _id: 0,
            artist: "$_id",
            avg_popularity: { $round: ["$avg_popularity", 1] }
        }
    }
];

const topArtists = currentDb.tracks.aggregate(topArtistsPipeline).toArray();
printjson(topArtists);
console.log("\n" + "=".repeat(50) + "\n");


// =========================================================================
// Завдання 2. Розподіл треків за настроєм
// =========================================================================
console.log("--- Завдання 2: Розподіл треків за настроєм ---");

const moodDistributionPipeline = [
    {
        $project: {
            mood: {
                $cond: {
                    // Перевірка на високий valence (> 0.5)
                    if: { $gt: ["$audio_features.valence", 0.5] },
                    then: {
                        $cond: {
                            if: { $gt: ["$audio_features.energy", 0.5] },
                            then: "happy",
                            else: "calm"
                        }
                    },
                    // Блок else: низький valence (<= 0.5)
                    else: {
                        $cond: {
                            if: { $gt: ["$audio_features.energy", 0.5] },
                            then: "angry",
                            else: "sad"
                        }
                    }
                }
            }
        }
    },
    {
        $group: {
            _id: "$mood",
            track_count: { $sum: 1 }
        }
    },
    { $sort: { track_count: -1 } },
    {
        $project: {
            _id: 0,
            mood: "$_id",
            track_count: 1
        }
    }
];

const moodDistribution = currentDb.tracks.aggregate(moodDistributionPipeline).toArray();
printjson(moodDistribution);
console.log("\n" + "=".repeat(50) + "\n");


// =========================================================================
// Завдання 3. Найбільш «танцювальний» жанр
// =========================================================================
console.log("--- Завдання 3: Найбільш танцювальний жанр (Топ-5 для наочності) ---");

const danceableGenrePipeline = [
    {
        $group: {
            _id: "$track_genre",
            track_count: { $sum: 1 },
            avg_danceability: { $avg: "$audio_features.danceability" },
            avg_energy: { $avg: "$audio_features.energy" },
            avg_valence: { $avg: "$audio_features.valence" }
        }
    },
    { $match: { track_count: { $gte: 100 } } },
    // Сортуємо за танцювальністю, щоб дізнатися лідера
    { $sort: { avg_danceability: -1 } },
    { $limit: 5 }, // беремо лідерів для красивого виводу
    {
        $project: {
            _id: 0,
            genre: "$_id",
            avg_danceability: { $round: ["$avg_danceability", 3] },
            avg_energy: { $round: ["$avg_energy", 3] },
            avg_valence: { $round: ["$avg_valence", 3] },
            track_count: 1
        }
    }
];

const danceableGenres = currentDb.tracks.aggregate(danceableGenrePipeline).toArray();
printjson(danceableGenres);
console.log("\n=== АНАЛІТИЧНІ ЗАПИТИ ВИТРЕНОВАНО УСПІШНО ===");