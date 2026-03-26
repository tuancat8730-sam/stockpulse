"use client";

import { useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";

type Status = "loading" | "success" | "error";

export default function AuthCallbackPage() {
  const searchParams = useSearchParams();
  const [status, setStatus] = useState<Status>("loading");
  const [errorMessage, setErrorMessage] = useState("");

  const botUsername = process.env.NEXT_PUBLIC_TELEGRAM_BOT_USERNAME;
  const apiUrl = process.env.NEXT_PUBLIC_API_URL;

  useEffect(() => {
    const code = searchParams.get("code");
    const state = searchParams.get("state");
    const error = searchParams.get("error");

    if (error) {
      setStatus("error");
      setErrorMessage("Đăng nhập Google bị huỷ hoặc gặp lỗi.");
      return;
    }

    if (!code || !state) {
      setStatus("error");
      setErrorMessage("Thiếu thông tin xác thực từ Google.");
      return;
    }

    // Forward code + state to FastAPI backend for token exchange
    fetch(`${apiUrl}/api/auth/callback?code=${code}&state=${state}`)
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
      })
      .then(() => setStatus("success"))
      .catch((err) => {
        console.error("Auth callback error:", err);
        setStatus("error");
        setErrorMessage("Không thể hoàn tất liên kết tài khoản. Vui lòng thử lại.");
      });
  }, [searchParams, apiUrl]);

  if (status === "loading") {
    return (
      <main className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="text-4xl mb-4">⏳</div>
          <p className="text-gray-600">Đang xử lý đăng nhập...</p>
        </div>
      </main>
    );
  }

  if (status === "error") {
    return (
      <main className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center max-w-md mx-auto px-4">
          <div className="text-4xl mb-4">❌</div>
          <h1 className="text-xl font-semibold text-gray-800 mb-2">Liên kết thất bại</h1>
          <p className="text-gray-600 mb-6">{errorMessage}</p>
          {botUsername && (
            <a
              href={`https://t.me/${botUsername}`}
              className="inline-block bg-blue-500 text-white px-6 py-3 rounded-lg hover:bg-blue-600 transition-colors"
            >
              Quay lại Telegram
            </a>
          )}
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="text-center max-w-md mx-auto px-4">
        <div className="text-5xl mb-4">✅</div>
        <h1 className="text-2xl font-bold text-gray-800 mb-2">Liên kết thành công!</h1>
        <p className="text-gray-600 mb-6">
          Tài khoản Google đã được liên kết với Telegram của bạn.
          <br />
          Quay lại bot để tiếp tục thiết lập watchlist.
        </p>
        {botUsername && (
          <a
            href={`tg://resolve?domain=${botUsername}`}
            className="inline-block bg-blue-500 text-white px-6 py-3 rounded-lg hover:bg-blue-600 transition-colors"
          >
            Mở Telegram Bot →
          </a>
        )}
      </div>
    </main>
  );
}
