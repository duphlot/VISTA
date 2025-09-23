import { motion } from 'framer-motion';

export function LoadingAnimation() {
    return (
        <div className="w-full mx-auto max-w-3xl px-4 py-4">
            <div className="flex items-center justify-center">
                <BouncingDots />
            </div>
        </div>
    );
}

function BouncingDots() {
    return (
        <div className="flex items-center gap-1">
            {[0, 1, 2].map((index) => (
                <motion.div
                    key={index}
                    className="w-1.5 h-1.5 bg-gray-500 dark:bg-gray-400 rounded-full"
                    animate={{
                        y: [0, -4, 0],
                    }}
                    transition={{
                        duration: 0.6,
                        repeat: Infinity,
                        delay: index * 0.2,
                        ease: "easeInOut"
                    }}
                />
            ))}
        </div>
    );
}
