import React, { useState } from 'react';
import { iotService } from '../services/api';
import { Radio, Terminal, Volume2, CheckCircle2, AlertTriangle, Shield, Play } from 'lucide-react';

export const IoTMonitor: React.FC = () => {
  const [boxId, setBoxId] = useState('BOX-001');
  const [rfid, setRfid] = useState('RFID-1024');
  const [location, setLocation] = useState('Library');
  const [itemName, setItemName] = useState('Black Leather Wallet');
  const [category, setCategory] = useState('Wallet');
  const [color, setColor] = useState('Black');
  const [brand, setBrand] = useState('Wildhorn');
  const [desc, setDesc] = useState('Black leather wallet containing college identity card.');

  const [doorOpen, setDoorOpen] = useState(false);
  const [logLines, setLogLines] = useState<string[]>([
    '[SYSTEM] ESP32-WROOM-32 Virtual Hardware Simulator Initialized.',
    '[NET] Connected to Campus_WiFi (IP: 192.168.1.104)',
    '[RFID] MFRC-522 ready on SPI (SS: 21, RST: 22)',
    '[OLED] SSD1306 128x64 display calibrated on I2C (0x3C)',
    '[SERVO] SG90 Servo motor locked at 0°'
  ]);
  const [loading, setLoading] = useState(false);
  const [lastResult, setLastResult] = useState<any>(null);

  const triggerBuzzer = () => {
    try {
      const audioCtx = new (window.AudioContext || (window as any).webkitAudioContext)();
      const osc = audioCtx.createOscillator();
      const gain = audioCtx.createGain();
      osc.type = 'sine';
      osc.frequency.setValueAtTime(1800, audioCtx.currentTime);
      gain.gain.setValueAtTime(0.2, audioCtx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 0.15);
      osc.connect(gain);
      gain.connect(audioCtx.destination);
      osc.start();
      osc.stop(audioCtx.currentTime + 0.15);
    } catch (e) {}
  };

  const handleSimulateScan = async () => {
    setLoading(true);
    triggerBuzzer();
    setDoorOpen(true);

    const newLogs = [
      `[RFID] Tag Detected! UID: ${rfid}`,
      `[OLED] SSD1306: 'Tag Scanned: ${rfid}'`,
      `[SERVO] SG90 rotated to 90° (Door Unlocked)`,
      `[HTTP] Sending POST /api/iot/items to backend...`
    ];
    setLogLines(prev => [...prev, ...newLogs]);

    try {
      const res = await iotService.scanItem({
        box_id: boxId,
        rfid_id: rfid,
        location: location,
        item_name: itemName,
        category: category,
        color: color,
        brand: brand,
        description: desc
      });

      setLastResult(res.data);
      setLogLines(prev => [
        ...prev,
        `[HTTP 200 OK] Assigned ID: ${res.data.item_id}`,
        res.data.match_found ? `[AI ENGINE] 🎯 MATCH DETECTED! (${res.data.top_match_score}%)` : `[AI] Queued in lost/found index.`,
        `[SERVO] Auto-locking door back to 0° after 5s deposit.`
      ]);

      setTimeout(() => {
        setDoorOpen(false);
        triggerBuzzer();
      }, 5000);
    } catch (err: any) {
      setLogLines(prev => [...prev, `[ERROR] Failed to communicate with backend: ${err.message}`]);
      setDoorOpen(false);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-100 flex items-center gap-2.5">
          <Radio className="w-6 h-6 text-sky-400 animate-pulse" />
          Virtual ESP32 Hardware Simulator
        </h1>
        <p className="text-xs text-slate-400 mt-1">
          Emulates physical micro-controller hardware, MFRC-522 RFID scans, OLED screen feedback, and SG90 servo door actuators.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left: Virtual Hardware Device Display */}
        <div className="lg:col-span-6 space-y-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-slate-300">ESP32 HARDWARE DEVICE</span>
              <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-sky-500/10 text-sky-400 border border-sky-500/20">
                BOX-001 (ONLINE)
              </span>
            </div>

            {/* Simulated 0.96" SSD1306 OLED Screen */}
            <div className="bg-black border-2 border-slate-700 rounded-xl p-4 font-mono text-cyan-400 shadow-[inset_0_0_15px_rgba(6,182,212,0.15)]">
              <div className="flex justify-between border-b border-cyan-900/60 pb-1 text-[11px]">
                <span>TRACE AI SMART BOX</span>
                <span>📶 100%</span>
              </div>
              <div className="my-3 text-center">
                <div className="text-base font-bold text-slate-100">
                  {doorOpen ? 'DOOR UNLOCKED (90°)' : 'STATUS: READY TO SCAN'}
                </div>
                <div className="text-xs text-cyan-300 mt-1">
                  {doorOpen ? 'Please Deposit Item Inside' : 'Tap RFID Tag & Deposit Item'}
                </div>
              </div>
              <div className="flex justify-between border-t border-cyan-900/60 pt-1 text-[10px] text-cyan-500">
                <span>SERVO: {doorOpen ? 'OPEN (90°)' : 'LOCKED (0°)'}</span>
                <span>{location}</span>
              </div>
            </div>

            {/* Virtual Servo Door State Indicator */}
            <div className="p-4 bg-slate-950 rounded-xl border border-slate-800 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className={`w-3.5 h-3.5 rounded-full ${doorOpen ? 'bg-emerald-400 animate-ping' : 'bg-rose-500'}`} />
                <div>
                  <div className="text-xs font-bold text-slate-200">
                    Physical SG90 Drop Door: {doorOpen ? 'UNLOCKED (OPEN)' : 'LOCKED'}
                  </div>
                  <div className="text-[10px] text-slate-500">Auto-locks 5 seconds after RFID deposit.</div>
                </div>
              </div>
              <Volume2 className="w-4 h-4 text-slate-400" />
            </div>

            {/* Live Serial UART Log Terminal */}
            <div className="space-y-1.5">
              <div className="flex items-center gap-1.5 text-xs text-slate-400 font-mono">
                <Terminal className="w-3.5 h-3.5" /> ESP32 Serial Monitor (115200 Baud)
              </div>
              <div className="bg-slate-950 border border-slate-800 rounded-xl p-3 h-48 overflow-y-auto font-mono text-[11px] text-slate-300 space-y-1">
                {logLines.map((line, idx) => (
                  <div key={idx} className={line.includes('ERROR') ? 'text-rose-400' : line.includes('MATCH') ? 'text-purple-400 font-bold' : line.includes('HTTP 200') ? 'text-emerald-400' : 'text-slate-400'}>
                    {line}
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Right: Simulation Controls Form */}
        <div className="lg:col-span-6 space-y-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 space-y-4">
            <h3 className="font-bold text-slate-100 text-sm">Simulate RFID Tag Scan Event</h3>
            
            {/* Quick Demo Tag Pickers */}
            <div>
              <label className="block text-xs font-semibold text-slate-400 mb-1.5">Load Demo Test Tag:</label>
              <div className="grid grid-cols-2 gap-2">
                <button
                  type="button"
                  onClick={() => {
                    setRfid('RFID-1024');
                    setItemName('Black Leather Wallet');
                    setCategory('Wallet');
                    setColor('Black');
                    setBrand('Wildhorn');
                    setDesc('Black leather wallet containing college identity card found near library reading room.');
                  }}
                  className="p-2 bg-slate-950 hover:bg-slate-800 border border-slate-800 rounded-lg text-left text-xs text-slate-300 transition"
                >
                  <div className="font-bold text-sky-400">RFID-1024</div>
                  <div className="text-[10px] text-slate-500">Wildhorn Wallet (Match!)</div>
                </button>

                <button
                  type="button"
                  onClick={() => {
                    setRfid('RFID-E204A1');
                    setItemName('Boat Wireless Earbuds');
                    setCategory('Electronics');
                    setColor('White');
                    setBrand('Boat');
                    setDesc('White wireless earbuds inside a black silicone protective case.');
                  }}
                  className="p-2 bg-slate-950 hover:bg-slate-800 border border-slate-800 rounded-lg text-left text-xs text-slate-300 transition"
                >
                  <div className="font-bold text-sky-400">RFID-E204A1</div>
                  <div className="text-[10px] text-slate-500">Boat Earbuds (Match!)</div>
                </button>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">Target Box</label>
                <select
                  value={boxId}
                  onChange={(e) => setBoxId(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200"
                >
                  <option value="BOX-001">BOX-001 (Library)</option>
                  <option value="BOX-002">BOX-002 (Canteen)</option>
                  <option value="BOX-003">BOX-003 (Main Gate)</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">RFID UID Hex</label>
                <input
                  type="text"
                  value={rfid}
                  onChange={(e) => setRfid(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 font-mono"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-400 mb-1">Item Title</label>
              <input
                type="text"
                value={itemName}
                onChange={(e) => setItemName(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200"
              />
            </div>

            <button
              disabled={loading}
              onClick={handleSimulateScan}
              className="w-full py-3 bg-sky-600 hover:bg-sky-500 disabled:opacity-50 text-white rounded-xl text-xs font-bold flex items-center justify-center gap-2 shadow-lg shadow-sky-900/30 transition"
            >
              <Play className="w-4 h-4 fill-white" />
              {loading ? 'Transmitting Scan...' : 'Tap RFID & Deposit Item'}
            </button>

            {lastResult && (
              <div className="p-3 bg-slate-950 border border-slate-800 rounded-xl text-xs text-slate-300 space-y-1">
                <div><b>Assigned Item ID:</b> <span className="text-emerald-400 font-mono font-bold">{lastResult.item_id}</span></div>
                <div><b>Status:</b> {lastResult.message}</div>
                {lastResult.match_found && (
                  <div className="text-purple-400 font-bold">
                    🎯 AI Match Triggered: {lastResult.top_match_score}% Confidence!
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
