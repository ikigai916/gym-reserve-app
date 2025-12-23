// ローカルストレージでのユーザーID管理

const USER_ID_KEY = 'gym_reservation_user_id';

export function getUserId() {
  return localStorage.getItem(USER_ID_KEY);
}

export function setUserId(userId) {
  localStorage.setItem(USER_ID_KEY, userId);
}

export function removeUserId() {
  localStorage.removeItem(USER_ID_KEY);
}

