// queries/part2_queries.js
// Запуск: mongosh "ВАШ_URI" --file queries/part2_queries.js

const dbName = "spotify";
const currentDb = db.getSiblingDB(dbName);
console.log(`=== ВИКОНАННЯ ЗАПИТІВ ДО БАЗИ ДАНИХ: ${dbName} ===\n`);

// =========================================================================
// Завдання 1. Треки для вечірки
// =========================================================================
console.log("--- Завдання 1: Треки для вечірки (Перші 3 для прикладу) ---");

// 3 хвилини = 180 сек, 5 хвилин = 300 сек. Шукаємо у вкладеному audio_features
const partyTracks = currentDb.tracks.find({
    "audio_features.danceability": { $gt: 0.7 },
    "audio_features.energy": { $gt: 0.7 },
    "duration_sec": { $gte: 180, $lte: 300 }
}, {
    track_name: 1, 
    artists: 1, 
    "audio_features.danceability": 1, 
    "audio_features.energy": 1, 
    duration_sec: 1, 
    _id: 0
}).limit(3).toArray();

printjson(partyTracks);
console.log("\n" + "=".repeat(50) + "\n");


// =========================================================================
// Завдання 2. Виконавці, у яких усі треки популярні
// =========================================================================
console.log("--- Завдання 2: Топ-20 популярних артистів ---");

const popularArtistsPipeline = [
    // 1. Оскільки в полі artists лежить масив, «розгортаємо» його, щоб згрупувати по кожному артисту окремо
    { $unwind: "$artists" },
    // 2. Групуємо за іменем артиста та рахуємо метрики
    {
        $group: {
            _id: "$artists",
            total_tracks: { $sum: 1 },
            min_popularity: { $min: "$popularity" },
            avg_popularity: { $avg: "$popularity" }
        }
    },
    // 3. Фільтруємо за умовою: мінімум 3 треки, і мінімальна популярність >= 60
    {
        $match: {
            total_tracks: { $gte: 3 },
            min_popularity: { $gte: 60 }
        }
    },
    // 4. Сортуємо за середньою популярністю (від вищої до нижчої)
    { $sort: { avg_popularity: -1 } },
    // 5. Беремо Топ-20
    { $limit: 20 },
    // 6. Форматуємо вивід та округлюємо середнє значення до 1 знака
    {
        $project: {
            _id: 0,
            artist: "$_id",
            total_tracks: 1,
            min_popularity: 1,
            avg_popularity: { $round: ["$avg_popularity", 1] }
        }
    }
];

const popularArtists = currentDb.tracks.aggregate(popularArtistsPipeline).toArray();
printjson(popularArtists);
console.log("\n" + "=".repeat(50) + "\n");


// =========================================================================
// Завдання 3. Нетипові треки (Outliers за темпом)
// =========================================================================
console.log("--- Завдання 3: Нетипові треки за темпом (Приклад для декількох жанрів) ---");

const outlierTracksPipeline = [
    // 1. Спочатку групуємо за жанром, щоб порахувати середнє (mean) та стандартне відхилення (stdDev)
    // А також збираємо всі треки жанру в масив за допомогою $push, щоб потім відфільтрувати їх
    {
        $group: {
            _id: "$track_genre",
            avg_tempo: { $avg: "$audio_features.tempo" },
            std_dev_tempo: { $stdDevPop: "$audio_features.tempo" },
            all_tracks: {
                $push: {
                    _id: "$_id",
                    track_name: "$track_name",
                    popularity: "$popularity",
                    artists: "$artists",
                    audio_features: { tempo: "$audio_features.tempo" }
                }
            }
        }
    },
    // 2. Вираховуємо поріг аномальності (outlier_threshold = mean + 2 * stdDev)
    {
        $project: {
            _id: 0,
            genre: "$_id",
            avg_tempo: { $round: ["$avg_tempo", 1] },
            outlier_threshold: { 
                $round: [{ $add: ["$avg_tempo", { $multiply: [2, "$std_dev_tempo"] }] }, 1] 
            },
            // Фільтруємо масив треків, залишаючи лише ті, де темп вищий за поріг
            outlier_tracks: {
                $filter: {
                    input: "$all_tracks",
                    as: "track",
                    cond: { $gt: ["$$track.audio_features.tempo", { $add: ["$avg_tempo", { $multiply: [2, "$std_dev_tempo"] }] }] }
                }
            }
        }
    },
    // 3. Залишаємо лише ті жанри, де знайшлися такі аномальні треки
    { $match: { "outlier_tracks.0": { $exists: true } } },
    // Обмежуємо вивід двома жанрами для читабельності консолі, а всередині масиву беремо 1 трек
    { $limit: 2 },
    {
        $project: {
            genre: 1,
            avg_tempo: 1,
            outlier_threshold: 1,
            outlier_tracks: { $slice: ["$outlier_tracks", 1] } // показуємо лише один трек для зразка
        }
    }
];

const outlierTracks = currentDb.tracks.aggregate(outlierTracksPipeline).toArray();
printjson(outlierTracks);
console.log("\n" + "=".repeat(50) + "\n");


// =========================================================================
// Завдання 4: Треки для фонової роботи
// =========================================================================
console.log("--- Завдання 4: Треки для фонової роботи (Перші 3 для прикладу) ---");

const backgroundTracks = currentDb.tracks.find({
    "audio_features.loudness": { $lt: -10 },
    "audio_features.speechiness": { $lt: 0.1 },
    "audio_features.instrumentalness": { $gt: 0.5 },
    explicit: false
}, {
    track_name: 1,
    artists: 1,
    "audio_features.loudness": 1,
    "audio_features.speechiness": 1,
    "audio_features.instrumentalness": 1,
    explicit: 1,
    _id: 0
}).limit(3).toArray();

printjson(backgroundTracks);
console.log("\n=== ВИКОНАННЯ ЗАПИТІВ ЗАВЕРШЕНО ===");