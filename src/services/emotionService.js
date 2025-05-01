/**
 * Сервис для анализа эмоций и получения рекомендаций
 * В реальной реализации здесь будут API запросы к бэкенду с ИИ-анализом
 */

// Имитация API запроса для анализа эмоций
export const analyzeEmotion = async (text) => {
  // В реальном приложении это будет API запрос к серверу
  return new Promise((resolve) => {
    setTimeout(() => {
      // Генерация случайных данных об эмоциях
      const emotionsData = [
        { name: 'Радость', value: Math.floor(Math.random() * 100) },
        { name: 'Спокойствие', value: Math.floor(Math.random() * 100) },
        { name: 'Тревога', value: Math.floor(Math.random() * 100) },
        { name: 'Грусть', value: Math.floor(Math.random() * 100) },
        { name: 'Энергия', value: Math.floor(Math.random() * 100) },
      ];
      
      // Определение преобладающих эмоций
      const maxEmotion = emotionsData.reduce((prev, current) => {
        return prev.value > current.value ? prev : current;
      });
      
      const secondEmotion = emotionsData
        .filter(item => item.name !== maxEmotion.name)
        .reduce((prev, current) => {
          return prev.value > current.value ? prev : current;
        });
      
      const dominantEmotionText = maxEmotion.value > secondEmotion.value + 20 
        ? maxEmotion.name
        : `${maxEmotion.name} и ${secondEmotion.name}`;
      
      // Генерация рекомендаций на основе эмоций
      let suggestion = '';
      if (maxEmotion.name === 'Тревога' || maxEmotion.name === 'Грусть') {
        suggestion = 'Рекомендуем сегодня уделить время дыхательным упражнениям и медитации для снижения тревожности. Также будет полезна прогулка на свежем воздухе.';
      } else if (maxEmotion.name === 'Радость' || maxEmotion.name === 'Энергия') {
        suggestion = 'Отличное состояние! Используйте эту энергию для творчества или физической активности. Запланируйте что-то приятное на вечер.';
      } else {
        suggestion = 'Сегодня хороший день для рефлексии и планирования. Уделите время любимому хобби, чтобы поддержать баланс эмоций.';
      }
      
      // Формирование результата анализа
      const result = {
        emotionsData,
        analysis: {
          dominantEmotion: dominantEmotionText,
          summary: `Ваше эмоциональное состояние характеризуется преобладанием ${dominantEmotionText.toLowerCase()}. ${
            maxEmotion.name === 'Тревога' || maxEmotion.name === 'Грусть' 
              ? 'Обратите внимание на техники самопомощи.'
              : 'Это хороший эмоциональный фон.'
          }`,
          suggestion
        }
      };
      
      resolve(result);
    }, 1000); // Имитация задержки сети
  });
};

// Получение истории записей
export const getEntryHistory = async () => {
  // В реальном приложении это будет запрос к API/базе данных
  return new Promise((resolve) => {
    setTimeout(() => {
      const mockEntries = [
        {
          id: 1,
          date: '01.05.2025',
          content: 'Сегодня был продуктивный день, но я немного устал от работы. Всё же чувствую удовлетворение от проделанной работы.',
          dominantEmotion: 'Удовлетворение',
        },
        {
          id: 2,
          date: '30.04.2025',
          content: 'День был напряженным, много дедлайнов. Чувствую небольшое беспокойство о завтрашней встрече.',
          dominantEmotion: 'Тревога',
        },
        {
          id: 3,
          date: '29.04.2025',
          content: 'Отличный день! Много общался с друзьями, хорошая погода поднимает настроение.',
          dominantEmotion: 'Радость',
        },
      ];
      
      resolve(mockEntries);
    }, 500);
  });
};

// Получение премиум-рекомендаций для пользователя
export const getPremiumRecommendations = async (emotionData) => {
  // В реальном приложении это будет запрос к API для получения персонализированных рекомендаций
  return new Promise((resolve) => {
    setTimeout(() => {
      const recommendations = [
        {
          id: 1,
          title: 'Управление стрессом',
          description: 'Персонализированная программа для снижения тревожности на основе данных вашего профиля',
          type: 'premium',
        },
        {
          id: 2,
          title: 'Медитация осознанности',
          description: '10-минутная медитация для восстановления эмоционального баланса',
          type: 'premium',
        },
        {
          id: 3,
          title: 'Техники когнитивно-поведенческой терапии',
          description: 'Упражнения для работы с негативными мыслями',
          type: 'premium',
        },
      ];
      
      resolve(recommendations);
    }, 500);
  });
};