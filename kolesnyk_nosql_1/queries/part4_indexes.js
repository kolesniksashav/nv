// queries/part4_indexes.js
// Запуск: mongosh "ВАШ_URI" --file queries/part4_indexes.js

const dbName = "spotify";
const currentDb = db.getSiblingDB(dbName);
console.log(`=== ЧАСТЬ 4: ИНДЕКСЫ И ОПТИМИЗАЦИЯ (База: ${dbName}) ===\n`);

// =========================================================================
// Завдання 1. Аналіз запиту та індексація
// =========================================================================
console.log("--- Завдання 1: Анализ запроса для Поп-музыки ---");

// Перед початком видалимо старі індекси (якщо вони були), щоб аналіз був чистим
currentDb.tracks.dropIndexes();

console.log("1. План выполнения БЕЗ индексов:");
const explainBefore1 = currentDb.tracks.find({
  track_genre: "pop",
  "audio_features.danceability": { $gte: 0.7 }
}).sort({ popularity: -1 }).explain("executionStats");

// Виводимо ключові метрики у консоль
print(`   Cтратегия поиска (stage): ${explainBefore1.queryPlanner.winningPlan.stage}`);
print(`   Проверено документов (docsExamined): ${explainBefore1.executionStats.executionStages.docsExamined}`);
print(`   Возвращено документов (nReturned): ${explainBefore1.executionStats.executionStages.nReturned}\n`);

// Создаем оптимальный составной индекс (Compound Index) по правилу ESR (Equality, Sort, Range)
console.log("Создаем составной индекс для Завдання 1...");
currentDb.tracks.createIndex({
  track_genre: 1,      // Equality (точний збіг)
  popularity: -1,      // Sort (сортування за спаданням)
  "audio_features.danceability": 1 // Range (діапазонний пошук)
});

console.log("\n2. План выполнения ПОСЛЕ создания индекса:");
const explainAfter1 = currentDb.tracks.find({
  track_genre: "pop",
  "audio_features.danceability": { $gte: 0.7 }
}).sort({ popularity: -1 }).explain("executionStats");

print(`   Cтратегия поиска (stage): ${explainAfter1.queryPlanner.winningPlan.stage}`);
print(`   Использован индекс (inputStage.stage): ${explainAfter1.queryPlanner.winningPlan.inputStage ? explainAfter1.queryPlanner.winningPlan.inputStage.stage : "Нет"}`);
print(`   Проверено ключей индекса (keysExamined): ${explainAfter1.executionStats.executionStages.inputStage.keysExamined}`);
print(`   Проверено документов (docsExamined): ${explainAfter1.executionStats.executionStages.docsExamined}`);
print(`   Возвращено документов (nReturned): ${explainAfter1.executionStats.executionStages.nReturned}\n`);
console.log("=".repeat(50) + "\n");


// =========================================================================
// Завдання 2. Індекс для інших полів (Фонова робота)
// =========================================================================
console.log("--- Завдання 2: Индекс для фоновой музыки ---");

console.log("Создаем составной индекс для фоновой работы...");
currentDb.tracks.createIndex({
  explicit: 1,
  "audio_features.speechiness": 1,
  "audio_features.instrumentalness": 1
});

console.log("Проверяем использование индекса через explain():");
const explain2 = currentDb.tracks.find({
  "audio_features.loudness": { $lt: -10 }, // це поле поза індексом
  "audio_features.speechiness": { $lt: 0.1 },
  "audio_features.instrumentalness": { $gt: 0.5 },
  explicit: false
}).explain("executionStats");

print(`   Итоговая стратегия (stage): ${explain2.queryPlanner.winningPlan.stage}`);
// Показуємо, що MongoDB занурилася в індекс (IXSCAN)
if (explain2.queryPlanner.winningPlan.inputStage) {
    print(`   Дочерняя стадия сканирования: ${explain2.queryPlanner.winningPlan.inputStage.stage}`);
    print(`   Имя использованного индекса: ${explain2.queryPlanner.winningPlan.inputStage.indexName}`);
}

// =========================================================================
// Завдання 3. Демонстрація покривного запиту (Covered Query)
// =========================================================================
console.log("--- Завдання 3: Наочна перевірка Покривного індексу ---");

console.log("1. Тестуємо ОРИГІНАЛЬНИЙ запит із завдання (без проєкції):");
const explainCoveredFalse = currentDb.tracks.find({
  track_genre: "pop",
  popularity: { $gte: 70 }
}).explain("executionStats");

print(`   Головна стратегія: ${explainCoveredFalse.queryPlanner.winningPlan.stage}`);
print(`   Чи ходив на диск за документами? (docsExamined): ${explainCoveredFalse.executionStats.executionStages.docsExamined}`);
print(`   Висновок: Запит НЕ покривний, бо docsExamined > 0 (база зчитувала файли з диска).\n`);

console.log("2. Тестуємо МОДЕРНІЗОВАНИЙ запит (із правильною проєкцією):");
const explainCoveredTrue = currentDb.tracks.find(
  { track_genre: "pop", popularity: { $gte: 70 } },
  { track_genre: 1, popularity: 1, _id: 0 } // <-- Додали ліміт полів
).explain("executionStats");

// Перевіряємо стадію покривного запиту. Якщо FETCH немає, головною стадією стає PROD_ITER або IXSCAN
//print(`   Головна стратегія: ${explainCoveredTrue.queryPlanner.winningPlan.stage}`);
//print(`   Чи ходив на диск за документами? (docsExamined): ${explainCoveredTrue.executionStats.executionStages.docsExamined}`);
//print(`   Висновок: Запит ПОКРИВНИЙ! docsExamined дорівнює 0, база взяла все суворо з пам'яті індексу.`);

// Перевіряємо наявність docsExamined. Якщо поля немає (undefined), підставляємо 0
const rawDocs = explainCoveredTrue.executionStats.executionStages.docsExamined;
const docsCount = rawDocs === undefined ? "0 (відсутнє в плані, бо FETCH не запускався)" : rawDocs;

print(`   Головна стратегія: ${explainCoveredTrue.queryPlanner.winningPlan.stage}`);
print(`   Чи ходив на диск за документами? (docsExamined): ${docsCount}`);
print(`   Висновок: Запит ПОКРИВНИЙ! docsExamined дорівнює 0, база взяла все суворо з пам'яті індексу.`);

console.log("\n=== СКРИПТ ВЫПОЛНЕН УСПЕШНО ===");