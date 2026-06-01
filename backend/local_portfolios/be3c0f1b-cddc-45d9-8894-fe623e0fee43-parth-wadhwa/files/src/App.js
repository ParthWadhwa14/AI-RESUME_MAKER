import React from 'react';
import { useState } from 'react';
import { motion } from 'framer-motion';
import { FiArrowRight } from 'lucide-react';

function App() {
  const [count, setCount] = useState(0);
  return (
    <div className="max-w-md mx-auto p-4 md:p-6 lg:p-8 bg-gray-900 text-white">
      <h1 className="text-5xl font-bold mb-4">Hero Section</h1>
      <p className="text-lg mb-4">Lorem ipsum dolor sit amet, consectetur adipiscing elit.</p>
      <button className="bg-orange-500 hover:bg-orange-700 text-white font-bold py-2 px-4 rounded" onClick={() => setCount(count + 1)}>
        Click me
      </button>
      <p className="text-lg mt-4">Count: {count}</p>
      <motion.div initial={{ x: -100 }} animate={{ x: 0 }} transition={{ duration: 0.5 }} className="mt-4">
        <h2 className="text-3xl font-bold mb-2">Card Section</h2>
        <div className="flex flex-wrap justify-center">
          <div className="w-full md:w-1/2 xl:w-1/3 p-4">
            <div className="bg-gray-800 p-4 rounded">
              <h3 className="text-lg font-bold mb-2">Card 1</h3>
              <p className="text-sm mb-2">Lorem ipsum dolor sit amet, consectetur adipiscing elit.</p>
              <button className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded">
                Learn more
              </button>
            </div>
          </div>
          <div className="w-full md:w-1/2 xl:w-1/3 p-4">
            <div className="bg-gray-800 p-4 rounded">
              <h3 className="text-lg font-bold mb-2">Card 2</h3>
              <p className="text-sm mb-2">Lorem ipsum dolor sit amet, consectetur adipiscing elit.</p>
              <button className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded">
                Learn more
              </button>
            </div>
          </div>
          <div className="w-full md:w-1/2 xl:w-1/3 p-4">
            <div className="bg-gray-800 p-4 rounded">
              <h3 className="text-lg font-bold mb-2">Card 3</h3>
              <p className="text-sm mb-2">Lorem ipsum dolor sit amet, consectetur adipiscing elit.</p>
              <button className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded">
                Learn more
              </button>
            </div>
          </div>
        </div>
      </motion.div>
    </div>
  );
}

export default App;