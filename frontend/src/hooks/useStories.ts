import { useState, useCallback } from 'react';

interface Story {
  id: string;
  title: string;
  content: string;
  moral: string;
  ageGroup: string;
  theme: string;
  videoUrl?: string;
  audioUrl?: string;
  duration?: number;
  characters?: string[];
  setting?: string;
  ageAppropriateWords?: string[];
  createdAt?: string;
}

export const useStories = () => {
  const [stories, setStories] = useState<Story[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const fetchStories = useCallback(async (ageGroup?: string, theme?: string) => {
    try {
      setLoading(true);
      setError('');
      
      const params = new URLSearchParams();
      if (ageGroup) params.append('age_group', ageGroup);
      if (theme) params.append('theme', theme);
      
      const response = await fetch(`/api/stories?${params.toString()}`);
      
      if (!response.ok) {
        throw new Error('गोष्टी लोड करताना समस्या आली');
      }
      
      const data = await response.json();
      setStories(data);
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'काहीतरी चूक झाली');
      // For development, provide sample data
      setStories(getSampleStories());
    } finally {
      setLoading(false);
    }
  }, []);

  const createStory = useCallback(async (storyData: {
    age_group: string;
    theme: string;
    moral_type: string;
  }) => {
    try {
      setLoading(true);
      setError('');
      
      const response = await fetch('/api/stories/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(storyData),
      });
      
      if (!response.ok) {
        throw new Error('गोष्ट तयार करताना समस्या आली');
      }
      
      const newStory = await response.json();
      setStories(prev => [newStory, ...prev]);
      
      return newStory;
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'काहीतरी चूक झाली');
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  return {
    stories,
    loading,
    error,
    fetchStories,
    createStory,
  };
};

// Sample data for development
const getSampleStories = (): Story[] => [
  {
    id: 'sample-1',
    title: 'लहान मुंगी आणि मोठा हत्ती',
    content: `एकदा एका जंगलात एक लहान मुंगी राहत होती. ती खूप मेहनती होती. दररोज ती अन्न गोळा करत होती.

एक दिवशी एक मोठा हत्ती त्या जंगलात आला. तो खूप गर्विष्ठ होता. त्याने मुंगीला म्हटले, "अरे लहान मुंगी, तू इतकी छोटी आहेस! तुझ्यापासून काय होणार?"

मुंगी शांतपणे म्हणाली, "आकार महत्वाचा नाही, कर्म महत्वाचे आहे."

काही दिवसांनी हत्ती एका जाळ्यात अडकला. तो मदतीसाठी ओरडू लागला. लहान मुंगीने हे ऐकले आणि लगेच मदतीला धावली.

मुंगीने आपल्या तीक्ष्ण दातांनी जाळे कापले आणि हत्तीला मुक्त केले.

हत्तीला आपल्या चुकीची जाणीव झाली. त्याने मुंगीचे आभार मानले.`,
    moral: 'आकार किंवा शक्ती महत्वाची नाही, मदत करण्याची इच्छा महत्वाची आहे. लहान असलो तरी आपण मोठी मदत करू शकतो.',
    ageGroup: '5-7',
    theme: 'मदत',
    duration: 180,
    characters: ['मुंगी', 'हत्ती'],
    setting: 'जंगल',
    ageAppropriateWords: ['मेहनती', 'गर्विष्ठ', 'तीक्ष्ण'],
    createdAt: new Date().toISOString()
  },
  {
    id: 'sample-2',
    title: 'सत्यवादी राजा',
    content: `एकदा एक राजा होता. तो नेहमी सत्य बोलत असे. त्याच्या राज्यात सर्व लोक त्याचा आदर करत.

एक दिवशी एक व्यापारी राजाकडे आला. त्याने राजाला सोन्याचे दागिने दाखवले. "हे खरे सोने आहे," असे तो म्हणाला.

राजाने दागिने तपासले. ते खोटे होते. राजा म्हणाला, "हे सोने खरे नाही. तू खोटे बोलत आहेस."

व्यापारी लाजला. त्याने राजाला सत्य सांगितले. राजाने त्याला माफ केले आणि सत्य बोलण्याचे महत्व समजावले.

त्या दिवसापासून व्यापारी नेहमी सत्य बोलू लागला.`,
    moral: 'सत्य बोलणे हे सर्वात मोठे गुण आहे. सत्य बोलल्याने सर्वांचा आदर मिळतो.',
    ageGroup: '8-12',
    theme: 'प्रामाणिकता',
    duration: 150,
    characters: ['राजा', 'व्यापारी'],
    setting: 'राजमहल',
    ageAppropriateWords: ['सत्यवादी', 'व्यापारी', 'दागिने'],
    createdAt: new Date().toISOString()
  },
  {
    id: 'sample-3',
    title: 'मित्राची मदत',
    content: `रामू आणि श्यामू हे दोन चांगले मित्र होते. ते रोज एकत्र खेळत.

एक दिवशी रामू दुःखी होता. त्याचे खेळणे तुटले होते. श्यामूने हे पाहिले.

श्यामू म्हणाला, "रामू, तू का दुःखी आहेस?" रामूने आपले तुटलेले खेळणे दाखवले.

श्यामूने आपले खेळणे रामूला दिले. "आपण एकत्र खेळू," असे तो म्हणाला.

रामू खूप आनंदी झाला. त्यांनी एकत्र खेळ खेळला.`,
    moral: 'खरे मित्र एकमेकांची मदत करतात. मैत्री हे जगातील सर्वात सुंदर भावना आहे.',
    ageGroup: '2-4',
    theme: 'मैत्री',
    duration: 120,
    characters: ['रामू', 'श्यामू'],
    setting: 'खेळाचे मैदान',
    ageAppropriateWords: ['मित्र', 'खेळणे', 'आनंदी'],
    createdAt: new Date().toISOString()
  }
];