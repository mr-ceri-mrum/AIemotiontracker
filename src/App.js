import { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import { Calendar, MessageSquare, Home, Settings, User, Award } from 'lucide-react';

const App = () => {
  const [activeTab, setActiveTab] = useState('home');
  const [journalEntry, setJournalEntry] = useState('');
  const [entries, setEntries] = useState([]);
  const [userProfile, setUserProfile] = useState({
    name: 'Пользователь',
    streakDays: 7,
    premium: false,
  });
  
  // Placeholder emotions data
  const [emotionsData, setEmotionsData] = useState([
    { name: 'Радость', value: 60 },
    { name: 'Спокойствие', value: 70 },
    { name: 'Тревога', value: 30 },
    { name: 'Грусть', value: 20 },
    { name: 'Энергия', value: 55 },
  ]);
  
  const [analysisResult, setAnalysisResult] = useState({
    dominantEmotion: 'Радость и спокойствие',
    summary: 'Сегодня у вас преобладают позитивные эмоции. Ваше общее эмоциональное состояние довольно сбалансированное, с некоторым уровнем тревожности.',
    suggestion: 'Попробуйте 10-минутную медитацию чтобы снизить тревожность и сохранить позитивный настрой.'
  });
  
  useEffect(() => {
    // Fetch previous entries
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
    ];
    setEntries(mockEntries);
  }, []);
  
  const analyzeEmotion = (text) => {
    // Simulate emotion analysis - in a real app this would be an API call
    if (!text.trim()) return;
    
    // Simulate processing delay
    setTimeout(() => {
      // Generate some random emotion data
      const newEmotionsData = [
        { name: 'Радость', value: Math.floor(Math.random() * 100) },
        { name: 'Спокойствие', value: Math.floor(Math.random() * 100) },
        { name: 'Тревога', value: Math.floor(Math.random() * 100) },
        { name: 'Грусть', value: Math.floor(Math.random() * 100) },
        { name: 'Энергия', value: Math.floor(Math.random() * 100) },
      ];
      
      setEmotionsData(newEmotionsData);
      
      // Determine dominant emotion
      const maxEmotion = newEmotionsData.reduce((prev, current) => {
        return prev.value > current.value ? prev : current;
      });
      
      const secondEmotion = newEmotionsData
        .filter(item => item.name !== maxEmotion.name)
        .reduce((prev, current) => {
          return prev.value > current.value ? prev : current;
        });
      
      const dominantEmotionText = maxEmotion.value > secondEmotion.value + 20 
        ? maxEmotion.name
        : `${maxEmotion.name} и ${secondEmotion.name}`;
      
      // Generate recommendation based on emotions
      let suggestion = '';
      if (maxEmotion.name === 'Тревога' || maxEmotion.name === 'Грусть') {
        suggestion = 'Рекомендуем сегодня уделить время дыхательным упражнениям и медитации для снижения тревожности. Также будет полезна прогулка на свежем воздухе.';
      } else if (maxEmotion.name === 'Радость' || maxEmotion.name === 'Энергия') {
        suggestion = 'Отличное состояние! Используйте эту энергию для творчества или физической активности. Запланируйте что-то приятное на вечер.';
      } else {
        suggestion = 'Сегодня хороший день для рефлексии и планирования. Уделите время любимому хобби, чтобы поддержать баланс эмоций.';
      }
      
      setAnalysisResult({
        dominantEmotion: dominantEmotionText,
        summary: `Ваше эмоциональное состояние характеризуется преобладанием ${dominantEmotionText.toLowerCase()}. ${
          maxEmotion.name === 'Тревога' || maxEmotion.name === 'Грусть' 
            ? 'Обратите внимание на техники самопомощи.'
            : 'Это хороший эмоциональный фон.'
        }`,
        suggestion
      });
      
      // Add entry to history
      const newEntry = {
        id: entries.length + 1,
        date: new Date().toLocaleDateString('ru-RU'),
        content: text,
        dominantEmotion: dominantEmotionText,
      };
      
      setEntries([newEntry, ...entries]);
      
    }, 500);
  };
  
  const handleSubmit = (e) => {
    if (e && e.preventDefault) {
      e.preventDefault();
    }
    if (journalEntry.trim()) {
      analyzeEmotion(journalEntry);
      // Don't clear the entry until analysis is complete
    }
  };
  
  // Main Tabs
  const renderContent = () => {
    switch (activeTab) {
      case 'home':
        return (
          <div className="p-4 space-y-8">
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-semibold mb-4">Дневник эмоций</h2>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Как прошел ваш день? Поделитесь своими мыслями и чувствами
                  </label>
                  <textarea
                    className="w-full px-3 py-2 text-gray-700 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    rows="5"
                    value={journalEntry}
                    onChange={(e) => setJournalEntry(e.target.value)}
                    placeholder="Сегодня я чувствую..."
                  />
                </div>
                <button
                  onClick={handleSubmit}
                  className="w-full bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded-lg transition-colors"
                >
                  Анализировать
                </button>
              </div>
            </div>
            
            {analysisResult && (
              <div className="bg-white rounded-lg shadow p-6">
                <h2 className="text-xl font-semibold mb-4">Анализ эмоций</h2>
                <div className="mb-6">
                  <div className="mb-2 text-sm font-medium text-gray-700">
                    Преобладающие эмоции: <span className="font-bold text-blue-600">{analysisResult.dominantEmotion}</span>
                  </div>
                  <div className="h-64 w-full">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={emotionsData}>
                        <XAxis dataKey="name" />
                        <YAxis />
                        <Tooltip />
                        <Bar dataKey="value" fill="#4F46E5" />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                </div>
                
                <div className="space-y-4">
                  <div>
                    <h3 className="font-medium text-gray-900">Резюме:</h3>
                    <p className="text-gray-700">{analysisResult.summary}</p>
                  </div>
                  <div>
                    <h3 className="font-medium text-gray-900">Рекомендация:</h3>
                    <p className="text-gray-700">{analysisResult.suggestion}</p>
                  </div>
                  {!userProfile.premium && (
                    <div className="mt-4 p-3 bg-blue-50 rounded-lg border border-blue-200">
                      <p className="text-sm text-blue-800">
                        <span className="font-bold">Подключите премиум</span> для получения персонализированных рекомендаций от психологов и доступа к упражнениям
                      </p>
                      <button className="mt-2 bg-blue-600 hover:bg-blue-700 text-white text-sm py-1 px-3 rounded">
                        Узнать больше
                      </button>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        );
        
      case 'history':
        return (
          <div className="p-4">
            <h2 className="text-xl font-semibold mb-4">История записей</h2>
            <div className="space-y-4">
              {entries.map((entry) => (
                <div key={entry.id} className="bg-white rounded-lg shadow p-4">
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-sm text-gray-500">{entry.date}</span>
                    <span className="px-2 py-1 text-xs rounded-full bg-blue-100 text-blue-800">
                      {entry.dominantEmotion}
                    </span>
                  </div>
                  <p className="text-gray-700">{entry.content}</p>
                </div>
              ))}
            </div>
          </div>
        );
        
      case 'insights':
        return (
          <div className="p-4">
            <h2 className="text-xl font-semibold mb-4">Инсайты и тренды</h2>
            <div className="bg-white rounded-lg shadow p-4">
              <h3 className="font-medium text-gray-900 mb-2">Недельная динамика эмоций</h3>
              <div className="h-64 w-full bg-gray-100 rounded flex items-center justify-center text-gray-500">
                Графики эмоций за неделю (доступно в премиум)
              </div>
            </div>
            
            <div className="bg-white rounded-lg shadow p-4 mt-4">
              <h3 className="font-medium text-gray-900 mb-2">Рекомендации психологов</h3>
              <div className="space-y-2">
                <div className="p-3 border rounded-lg">
                  <h4 className="font-medium">Управление стрессом</h4>
                  <p className="text-sm text-gray-700">Практики осознанности и глубокого дыхания могут снизить уровень тревожности</p>
                </div>
                <div className="p-3 border rounded-lg">
                  <h4 className="font-medium">Улучшение сна</h4>
                  <p className="text-sm text-gray-700">Рекомендации для здорового сна и восстановления</p>
                </div>
                <div className="p-3 border rounded-lg">
                  <h4 className="font-medium">Работа с негативными мыслями</h4>
                  <p className="text-sm text-gray-700">Техники когнитивно-поведенческой терапии</p>
                </div>
              </div>
            </div>
          </div>
        );
        
      case 'profile':
        return (
          <div className="p-4">
            <h2 className="text-xl font-semibold mb-4">Ваш профиль</h2>
            <div className="bg-white rounded-lg shadow p-4">
              <div className="flex items-center space-x-4 mb-6">
                <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center">
                  <User size={32} className="text-blue-600" />
                </div>
                <div>
                  <h3 className="font-medium text-lg">{userProfile.name}</h3>
                  <div className="flex items-center text-sm text-gray-500">
                    <Award size={16} className="mr-1 text-yellow-500" />
                    <span>{userProfile.streakDays} дней подряд</span>
                  </div>
                </div>
              </div>
              
              <div className="space-y-4">
                <div className="border-t pt-4">
                  <h3 className="font-medium text-gray-900 mb-2">Настройки</h3>
                  <div className="space-y-2">
                    <div className="flex justify-between items-center p-2 hover:bg-gray-50 rounded">
                      <span>Уведомления</span>
                      <div className="relative">
                        <input type="checkbox" className="sr-only" id="toggle" defaultChecked />
                        <div className="w-10 h-4 bg-blue-200 rounded-full"></div>
                        <div className="dot absolute left-1 top-0 bg-blue-600 w-4 h-4 rounded-full transition-all"></div>
                      </div>
                    </div>
                    <div className="flex justify-between items-center p-2 hover:bg-gray-50 rounded">
                      <span>Темная тема</span>
                      <div className="relative">
                        <input type="checkbox" className="sr-only" id="theme-toggle" />
                        <div className="w-10 h-4 bg-gray-200 rounded-full"></div>
                        <div className="dot absolute left-0 top-0 bg-gray-400 w-4 h-4 rounded-full transition-all"></div>
                      </div>
                    </div>
                  </div>
                </div>
                
                <div className="border-t pt-4">
                  <h3 className="font-medium text-gray-900 mb-2">Подписка</h3>
                  <div className="bg-blue-50 p-3 rounded-lg border border-blue-200">
                    <p className="text-sm text-blue-800 mb-2">
                      {userProfile.premium 
                        ? 'У вас активна премиум подписка' 
                        : 'Перейдите на премиум для доступа к дополнительным функциям:'}
                    </p>
                    {!userProfile.premium && (
                      <ul className="text-sm text-blue-800 list-disc pl-5 mb-2">
                        <li>Персонализированные рекомендации</li>
                        <li>Углубленный анализ эмоций</li>
                        <li>Библиотека упражнений от психологов</li>
                        <li>Отсутствие рекламы</li>
                      </ul>
                    )}
                    <button className="bg-blue-600 hover:bg-blue-700 text-white text-sm py-1 px-3 rounded">
                      {userProfile.premium ? 'Управление подпиской' : 'Активировать премиум'}
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        );
        
      default:
        return <div>Загрузка...</div>;
    }
  };
  
  return (
    <div className="max-w-lg mx-auto bg-gray-50 min-h-screen flex flex-col">
      {/* Header */}
      <header className="bg-blue-600 text-white p-4">
        <h1 className="text-xl font-bold">AI Дневник Эмоций</h1>
      </header>
      
      {/* Main Content */}
      <main className="flex-1 overflow-y-auto pb-16">
        {renderContent()}
      </main>
      
      {/* Bottom Navigation */}
      <nav className="bg-white border-t fixed bottom-0 w-full max-w-lg">
        <div className="flex justify-around">
          <button 
            onClick={() => setActiveTab('home')}
            className={`p-4 flex flex-col items-center ${activeTab === 'home' ? 'text-blue-600' : 'text-gray-500'}`}
          >
            <Home size={20} />
            <span className="text-xs mt-1">Главная</span>
          </button>
          <button 
            onClick={() => setActiveTab('history')}
            className={`p-4 flex flex-col items-center ${activeTab === 'history' ? 'text-blue-600' : 'text-gray-500'}`}
          >
            <Calendar size={20} />
            <span className="text-xs mt-1">История</span>
          </button>
          <button 
            onClick={() => setActiveTab('insights')}
            className={`p-4 flex flex-col items-center ${activeTab === 'insights' ? 'text-blue-600' : 'text-gray-500'}`}
          >
            <MessageSquare size={20} />
            <span className="text-xs mt-1">Инсайты</span>
          </button>
          <button 
            onClick={() => setActiveTab('profile')}
            className={`p-4 flex flex-col items-center ${activeTab === 'profile' ? 'text-blue-600' : 'text-gray-500'}`}
          >
            <Settings size={20} />
            <span className="text-xs mt-1">Профиль</span>
          </button>
        </div>
      </nav>
    </div>
  );
};

export default App;