import express from 'express';
import cors from 'cors';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import { readFile, writeFile, mkdir } from 'fs/promises';
import { existsSync } from 'fs';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const app = express();
const PORT = 3001;

// データファイルのパス
const DATA_DIR = join(__dirname, '..', 'data');
const RESERVATIONS_FILE = join(DATA_DIR, 'reservations.json');
const USERS_FILE = join(DATA_DIR, 'users.json');

app.use(cors());
app.use(express.json());

// データディレクトリとファイルの初期化
async function initData() {
  if (!existsSync(DATA_DIR)) {
    await mkdir(DATA_DIR, { recursive: true });
  }
  if (!existsSync(RESERVATIONS_FILE)) {
    await writeFile(RESERVATIONS_FILE, JSON.stringify([], null, 2));
  }
  if (!existsSync(USERS_FILE)) {
    await writeFile(USERS_FILE, JSON.stringify([], null, 2));
  }
}

// 時間枠の生成（9:00-22:00の1時間単位）
function generateTimeSlots() {
  const slots = [];
  for (let hour = 9; hour < 22; hour++) {
    const start = `${hour.toString().padStart(2, '0')}:00`;
    const end = `${(hour + 1).toString().padStart(2, '0')}:00`;
    slots.push(`${start}-${end}`);
  }
  return slots;
}

// 予約データの読み込み
async function loadReservations() {
  try {
    const data = await readFile(RESERVATIONS_FILE, 'utf-8');
    return JSON.parse(data);
  } catch (error) {
    return [];
  }
}

// 予約データの保存
async function saveReservations(reservations) {
  await writeFile(RESERVATIONS_FILE, JSON.stringify(reservations, null, 2));
}

// ユーザーデータの読み込み
async function loadUsers() {
  try {
    const data = await readFile(USERS_FILE, 'utf-8');
    return JSON.parse(data);
  } catch (error) {
    return [];
  }
}

// ユーザーデータの保存
async function saveUsers(users) {
  await writeFile(USERS_FILE, JSON.stringify(users, null, 2));
}

// 今日の日付を YYYY-MM-DD 形式で取得
function getToday() {
  return new Date().toISOString().split('T')[0];
}

// 指定日の予約可能な時間枠を取得
app.get('/api/time-slots/:date', async (req, res) => {
  try {
    const { date } = req.params;
    const { userId } = req.query; // クエリパラメータでユーザーIDを取得（オプション）
    const today = getToday();

    // 過去の日付は予約不可
    if (date < today) {
      return res.json({ timeSlots: [], message: '過去の日付は予約できません' });
    }

    const reservations = await loadReservations();
    const allTimeSlots = generateTimeSlots();
    
    // アクティブな予約のみをフィルタリング
    const activeReservations = reservations.filter(r => 
      r.date === date && r.status === 'active'
    );

    const reservedTimeSlots = new Set(
      activeReservations.map(r => r.timeSlot)
    );

    const timeSlots = allTimeSlots.map(slot => {
      const reservation = activeReservations.find(r => r.timeSlot === slot);
      const isMyReservation = userId && reservation && reservation.userId === userId;
      
      return {
        slot,
        available: !reservedTimeSlots.has(slot),
        reservationId: reservation?.id || null,
        isMyReservation: isMyReservation || false
      };
    });

    res.json({ timeSlots });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// 予約作成
app.post('/api/reservations', async (req, res) => {
  try {
    const { userId, date, timeSlot } = req.body;

    if (!userId || !date || !timeSlot) {
      return res.status(400).json({ error: 'ユーザーID、日付、時間枠は必須です' });
    }

    // ユーザー情報を取得
    const users = await loadUsers();
    const user = users.find(u => u.id === userId);
    if (!user) {
      return res.status(404).json({ error: 'ユーザーが見つかりません' });
    }

    const today = getToday();
    if (date < today) {
      return res.status(400).json({ error: '過去の日付は予約できません' });
    }

    const reservations = await loadReservations();
    
    // 同じ日付・時間枠にアクティブな予約があるかチェック
    const conflict = reservations.find(r => 
      r.date === date && 
      r.timeSlot === timeSlot && 
      r.status === 'active'
    );

    if (conflict) {
      return res.status(409).json({ error: 'この時間枠は既に予約されています' });
    }

    const newReservation = {
      id: Date.now().toString(),
      userId,
      name: user.name, // ユーザー情報から名前を取得
      date,
      timeSlot,
      createdAt: new Date().toISOString(),
      status: 'active'
    };

    reservations.push(newReservation);
    await saveReservations(reservations);

    res.status(201).json(newReservation);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// 予約一覧取得（ユーザーIDでフィルタリング可能）
app.get('/api/reservations', async (req, res) => {
  try {
    const { userId } = req.query;
    const reservations = await loadReservations();
    
    let filtered = reservations.filter(r => r.status === 'active');
    
    if (userId) {
      filtered = filtered.filter(r => r.userId === userId);
    }

    res.json({ reservations: filtered });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// 予約キャンセル
app.delete('/api/reservations/:id', async (req, res) => {
  try {
    const { id } = req.params;
    const { userId } = req.query; // ユーザーIDで認証
    const reservations = await loadReservations();
    
    const index = reservations.findIndex(r => r.id === id);
    if (index === -1) {
      return res.status(404).json({ error: '予約が見つかりません' });
    }

    // 自分の予約かチェック
    if (userId && reservations[index].userId !== userId) {
      return res.status(403).json({ error: 'この予約をキャンセルする権限がありません' });
    }

    reservations[index].status = 'cancelled';
    await saveReservations(reservations);

    res.json({ message: '予約をキャンセルしました', reservation: reservations[index] });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// ユーザー作成
app.post('/api/users', async (req, res) => {
  try {
    const { name, email, phone } = req.body;

    if (!name) {
      return res.status(400).json({ error: '名前は必須です' });
    }

    const users = await loadUsers();
    
    // 既存のユーザーかチェック（メールアドレスがある場合）
    if (email) {
      const existingUser = users.find(u => u.email === email);
      if (existingUser) {
        return res.status(409).json({ error: 'このメールアドレスは既に登録されています' });
      }
    }

    const newUser = {
      id: Date.now().toString(),
      name,
      email: email || '',
      phone: phone || '',
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    };

    users.push(newUser);
    await saveUsers(users);

    res.status(201).json(newUser);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// ユーザー取得
app.get('/api/users/:id', async (req, res) => {
  try {
    const { id } = req.params;
    const users = await loadUsers();
    const user = users.find(u => u.id === id);

    if (!user) {
      return res.status(404).json({ error: 'ユーザーが見つかりません' });
    }

    res.json(user);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// ユーザー更新
app.put('/api/users/:id', async (req, res) => {
  try {
    const { id } = req.params;
    const { name, email, phone } = req.body;

    const users = await loadUsers();
    const index = users.findIndex(u => u.id === id);

    if (index === -1) {
      return res.status(404).json({ error: 'ユーザーが見つかりません' });
    }

    // メールアドレスの重複チェック（他のユーザーとの）
    if (email && users.some(u => u.id !== id && u.email === email)) {
      return res.status(409).json({ error: 'このメールアドレスは既に使用されています' });
    }

    // 更新
    if (name) users[index].name = name;
    if (email !== undefined) users[index].email = email;
    if (phone !== undefined) users[index].phone = phone;
    users[index].updatedAt = new Date().toISOString();

    await saveUsers(users);

    res.json(users[index]);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// サーバー起動
initData().then(() => {
  app.listen(PORT, () => {
    console.log(`サーバーが起動しました: http://localhost:${PORT}`);
  });
});

