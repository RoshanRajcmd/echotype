import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { CONSTANTS } from "./constants";

const Home: React.FC = () => {
    const [words] = useState(CONSTANTS.DEFAULT_PARAGRAPH.split(" "));
    const [showTest, setShowTest] = useState(false);
    const [currentIndex, setCurrentIndex] = useState(0);
    const [showWord, setShowWord] = useState("");
    const [enableWordFlash, setEnableWordFlash] = useState(true) //if set to true, will flash the word for a brif second
    const [typedWord, setTypedWord] = useState("");
    const [results, setResults] = useState<{ correct: boolean; word: string }[]>(
        []
    );
    const [startedAt, setStartedAt] = useState<number | null>(null);
    const [endedAt, setEndedAt] = useState<number | null>(null);

    // Start on first render
    const testStarted = () => {
        setShowTest(!showTest)
        if (!startedAt) {
            setStartedAt(Date.now());
            speakWord(words[0]);
        }
    };

    // Speak the word & show it briefly
    const speakWord = (word: string) => {
        const utterance = new SpeechSynthesisUtterance(word);
        utterance.rate = 0.9;
        utterance.rate = 1;     // speed (0.1–10, default = 1)
        utterance.pitch = 1;    // pitch (0–2, default = 1)

        // pick a voice
        const voices = speechSynthesis.getVoices();
        const selectedVoice = voices.find(v => v.name.includes("Google UK English"));
        if (selectedVoice) utterance.voice = selectedVoice;
        speechSynthesis.speak(utterance);

        setShowWord(word);
        setTimeout(() => setShowWord(""), 700); // word flashes briefly in millisecond
    };

    // Handle typing logic
    const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
        if (e.key === CONSTANTS.KEYS.QUIT) {
            setEndedAt(Date.now());
            return;
        }

        if (e.key === CONSTANTS.KEYS.NEXT_WORD && typedWord.trim() !== "") {
            const correct = typedWord.trim() === words[currentIndex];
            setResults((prev) => [...prev, { correct, word: typedWord.trim() }]);
            setTypedWord("");

            const nextIndex = currentIndex + 1;
            if (nextIndex < words.length) {
                setCurrentIndex(nextIndex);
                speakWord(words[nextIndex]);
            } else {
                setEndedAt(Date.now());
            }
        }
    };

    // Calculate WPM & Accuracy
    const getStats = () => {
        if (!startedAt || !endedAt) return null;
        const seconds = (endedAt - startedAt) / 1000;
        const minutes = seconds / 60;
        const wpm = Math.round(results.length / minutes);
        const accuracy =
            Math.round(
                (results.filter((r) => r.correct).length / results.length) * 100
            ) || 0;

        return { wpm, accuracy, time: seconds.toFixed(1) };
    };

    const stats = getStats();

    return (
        <div className="">

            <h1 className="mb-6 text-3xl font-bold underline">{CONSTANTS.APP.NAME}</h1>
            {!showTest ? (
                <button
                    className="w-4xl h-20 rounded-2xl border border-transparent px-5 py-2 text-6xl font-medium font-inherit bg-[#1a1a1a] cursor-pointer transition-colors duration-200 hover:border-amber-300 focus:outline focus:-outline-offset-0 focus:outline-[Highlight]"
                    onClick={() => testStarted()}>
                    Start
                </button>
            ) : (
                <AnimatePresence>
                    <motion.div
                        key="test-area"
                        initial={{ opacity: 0, y: 30 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0 }}
                        transition={{ duration: 0.6, ease: "easeOut" }}
                        className="w-full max-w-xl text-center space-y-4"
                    >
                        {endedAt ? (
                            <div className="p-4 border rounded shadow">
                                <h2 className="text-xl font-bold">Results</h2>
                                <p>WPM: {stats?.wpm}</p>
                                <p>Accuracy: {stats?.accuracy}%</p>
                                <p>Time: {stats?.time}s</p>
                            </div>
                        ) : (
                            <div className="">
                                {enableWordFlash && (
                                    <div className="text-2xl font-stretch-50% text-green-500 h-10">
                                        {showWord}
                                    </div>
                                )}

                                <input
                                    type="text"
                                    value={typedWord}
                                    onChange={(e) => setTypedWord(e.target.value)}
                                    onKeyDown={handleKeyDown}
                                    className="text-center items-center justify-center w-72 h-15 rounded-2xl border"
                                    placeholder="Type the word and press SPACE..."
                                    autoFocus
                                />
                                <div className="mt-6 text-sm text-gray-500">
                                    Press <kbd>Esc</kbd> to quit
                                </div>
                            </div>
                        )}

                        <div>
                            {results.map((res, idx) => (
                                <span key={idx} >
                                    {res.word}&nbsp;
                                </span>
                            ))}
                        </div>
                    </motion.div>
                </AnimatePresence>
            )}
        </div>
    );
};

export default Home;
