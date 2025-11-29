interface HeatmapData {
    hour: number;
    day: number;
    count: number;
}

const DAYS = ['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb'];
const HOURS = Array.from({ length: 24 }, (_, i) => i);

export function ActivityHeatmap({ data }: { data: HeatmapData[] }) {
    const getColor = (count: number, max: number) => {
        if (count === 0) return 'bg-gray-100 dark:bg-gray-800';
        const intensity = Math.min(count / max, 1);
        if (intensity < 0.2) return 'bg-blue-200 dark:bg-blue-900';
        if (intensity < 0.4) return 'bg-blue-300 dark:bg-blue-800';
        if (intensity < 0.6) return 'bg-blue-400 dark:bg-blue-700';
        if (intensity < 0.8) return 'bg-blue-500 dark:bg-blue-600';
        return 'bg-blue-600 dark:bg-blue-500';
    };

    const maxCount = Math.max(...data.map(d => d.count), 1);

    // Create grid
    const grid: Record<string, number> = {};
    data.forEach(d => {
        grid[`${d.day}-${d.hour}`] = d.count;
    });

    return (
        <div className="overflow-x-auto">
            <div className="inline-block min-w-full">
                <div className="flex gap-1">
                    <div className="flex flex-col gap-1 justify-around pr-2 text-xs text-muted-foreground">
                        {DAYS.map(day => (
                            <div key={day} className="h-6 flex items-center">{day}</div>
                        ))}
                    </div>
                    <div className="flex-1">
                        <div
                            className="grid gap-1 mb-1"
                            style={{ gridTemplateColumns: 'repeat(24, minmax(0, 1fr))' }}
                        >
                            {HOURS.map(hour => (
                                <div key={hour} className="text-[10px] text-center text-muted-foreground">
                                    {hour % 3 === 0 ? hour : ''}
                                </div>
                            ))}
                        </div>
                        <div className="space-y-1">
                            {DAYS.map((_, dayIndex) => (
                                <div
                                    key={dayIndex}
                                    className="grid gap-1"
                                    style={{ gridTemplateColumns: 'repeat(24, minmax(0, 1fr))' }}
                                >
                                    {HOURS.map(hour => {
                                        const count = grid[`${dayIndex}-${hour}`] || 0;
                                        return (
                                            <div
                                                key={hour}
                                                className={`h-8 rounded-sm ${getColor(count, maxCount)} transition-all hover:opacity-80 cursor-help relative group`}
                                                title={`${DAYS[dayIndex]} ${hour}:00 - ${count} mensagens`}
                                            />
                                        );
                                    })}
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
                <div className="mt-4 flex items-center gap-2 text-xs text-muted-foreground">
                    <span>Menos</span>
                    <div className="flex gap-1">
                        <div className="w-4 h-4 bg-gray-100 dark:bg-gray-800 rounded" />
                        <div className="w-4 h-4 bg-blue-200 dark:bg-blue-900 rounded" />
                        <div className="w-4 h-4 bg-blue-400 dark:bg-blue-700 rounded" />
                        <div className="w-4 h-4 bg-blue-600 dark:bg-blue-500 rounded" />
                    </div>
                    <span>Mais</span>
                </div>
            </div>
        </div>
    );
}
