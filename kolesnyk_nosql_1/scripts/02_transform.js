// scripts/02_transform.js
// Запуск: mongosh "MONGO_URI" --file scripts/02_transform.js

// 1. Створення/вибір бази даних та очищення старої колекції tracks
const dbName = "spotify";
const currentDb = db.getSiblingDB(dbName);

console.log(`Використовуємо базу даних: ${dbName}`);
currentDb.tracks.drop();
console.log("Стару колекцію tracks успішно видалено (якщо вона існувала).");

// Головний Aggregation Pipeline для трансформації даних
const pipeline = [
    {
        // Кроки 2, 4: Проєкція потрібних полів та формування вкладеного об'єкта
        $project: {
            _id: 1, // зберігаємо оригінальний ID документа
            track_id: 1,
            track_name: 1,
            album_name: 1,
            explicit: 1,
            popularity: 1,
            track_genre: 1,
            // Перейменовуємо artists на artists_raw для зручності подальшої обробки
            artists_raw: "$artists",
            
            // Формуємо вкладений об'єкт з аудіохарактеристиками
            audio_features: {
                danceability: "$danceability",
                energy: "$energy",
                loudness: "$loudness",
                speechiness: "$speechiness",
                acousticness: "$acousticness",
                instrumentalness: "$instrumentalness",
                liveness: "$liveness",
                valence: "$valence",
                tempo: "$tempo",
                key: "$key",
                mode: "$mode",
                time_signature: "$time_signature"
            },
            
            // Обчислюване поле: тривалість у секундах, округлена до 1 знака
            duration_sec: { 
                $round: [{ $divide: ["$duration_ms", 1000] }, 1] 
            },
            
            // Обчислюване поле: рівень популярності (popularity_tier)
            popularity_tier: {
                $cond: {
                    if: { $gte: ["$popularity", 70] },
                    then: "high",
                    else: {
                        $cond: {
                            if: { $gte: ["$popularity", 40] },
                            then: "medium",
                            else: "low"
                        }
                    }
                }
            }
        }
    },
    {
        // Крок 3: Перетворення рядка артистів на масив
        $addFields: {
            artists: {
                // $map перебирає кожен елемент масиву після розбиття і застосовує $trim
                $map: {
                    input: { $split: ["$artists_raw", ";"] },
                    as: "artist",
                    in: { $trim: { input: "$$artist" } }
                }
            }
        }
    },
    {
        // Крок 5: Очищення зайвих полів (прибираємо проміжний artists_raw)
        // Вихідні аудіофічі вже зникли, бо ми їх не включили на етапі $project
        $project: {
            artists_raw: 0
        }
    },
    {
        // Крок 6: Збереження результату у нову колекцію tracks
        $out: "tracks"
    }
];

// Запуск агрегації на сирій колекції
console.log("Запуск процесу трансформації через Aggregation Pipeline...");
currentDb.tracks_raw.aggregate(pipeline);
console.log("Трансформація завершена успішно!");

// Крок 7: Перевірка результату
const count = currentDb.tracks.countDocuments({});
console.log(`\n7. ПЕРЕВІРКА РЕЗУЛЬТАТУ:`);
console.log(`Кількість документів у колекції tracks: ${count}`);

console.log(`\nПриклад одного трансформованого документа:`);
const sampleDoc = currentDb.tracks.findOne();
printjson(sampleDoc);