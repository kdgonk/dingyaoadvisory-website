/**
 * 動態匯率轉換模組
 * 即時抓取 ZAR/TWD 匯率，自動轉換所有標記的金額
 */

(function() {
    'use strict';
    
    // 匯率快取
    let cachedRate = null;
    let lastFetchTime = null;
    const CACHE_DURATION = 60 * 60 * 1000; // 1 小時快取
    
    // 匯率 API（使用免費 API）
    const API_URL = 'https://api.exchangerate-api.com/v4/latest/ZAR';
    
    // 備用匯率（API 失敗時使用）
    const FALLBACK_RATE = 0.1675; // 1 ZAR ≈ 1.675 TWD（2026 年參考值）
    
    /**
     * 格式化數字為台幣格式
     */
    function formatTWD(amount) {
        if (amount >= 10000) {
            return 'NT$ ' + Math.round(amount / 10000) + ' 萬';
        }
        return 'NT$ ' + Math.round(amount).toLocaleString('zh-TW');
    }
    
    /**
     * 格式化 ZAR 金額
     */
    function formatZAR(amount) {
        return 'R ' + amount.toLocaleString('en-ZA');
    }
    
    /**
     * 抓取即時匯率
     */
    async function fetchExchangeRate() {
        // 檢查快取
        if (cachedRate && lastFetchTime && (Date.now() - lastFetchTime < CACHE_DURATION)) {
            return { rate: cachedRate, cached: true };
        }
        
        try {
            const response = await fetch(API_URL);
            const data = await response.json();
            
            if (data.rates && data.rates.TWD) {
                cachedRate = data.rates.TWD;
                lastFetchTime = Date.now();
                return { 
                    rate: cachedRate, 
                    cached: false,
                    fetchTime: new Date().toISOString()
                };
            } else {
                throw new Error('TWD rate not found');
            }
        } catch (error) {
            console.warn('匯率 API 失敗，使用備用匯率:', error.message);
            return { 
                rate: FALLBACK_RATE, 
                cached: false, 
                fallback: true,
                fetchTime: new Date().toISOString()
            };
        }
    }
    
    /**
     * 轉換所有標記的金額
     */
    async function convertAll() {
        const rateResult = await fetchExchangeRate();
        const rate = rateResult.rate;
        
        // 找出所有需要轉換的元素
        const elements = document.querySelectorAll('[data-zar]');
        
        elements.forEach(el => {
            const zar = parseFloat(el.getAttribute('data-zar'));
            const twd = zar * rate;
            
            // 更新內容
            const originalText = el.textContent;
            
            // 檢查是否有自定義格式
            if (el.getAttribute('data-format') === 'short') {
                el.textContent = '約 ' + formatTWD(twd);
            } else if (el.getAttribute('data-format') === 'table') {
                el.textContent = formatTWD(twd);
            } else {
                el.textContent = '約新台幣 ' + Math.round(twd / 10000) + ' 萬元';
            }
        });
        
        // 更新匯率時間戳記
        const timestampElements = document.querySelectorAll('[data-exchange-time]');
        timestampElements.forEach(el => {
            const time = new Date();
            el.textContent = '參考匯率更新時間：' + time.toLocaleString('zh-TW', {
                year: 'numeric',
                month: 'long',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            });
        });
        
        // 顯示匯率來源
        const sourceElements = document.querySelectorAll('[data-exchange-source]');
        sourceElements.forEach(el => {
            if (rateResult.fallback) {
                el.textContent = '（使用參考匯率）';
            } else {
                el.textContent = '（即時匯率）';
            }
        });
        
        return rateResult;
    }
    
    /**
     * 顯示匯率資訊區塊
     */
    function showExchangeInfo(rateResult) {
        const infoBlocks = document.querySelectorAll('.exchange-rate-info');
        infoBlocks.forEach(block => {
            const rateEl = block.querySelector('.rate-value');
            const timeEl = block.querySelector('.rate-time');
            
            if (rateEl) {
                rateEl.textContent = '1 ZAR ≈ ' + rateResult.rate.toFixed(4) + ' TWD';
            }
            if (timeEl) {
                timeEl.textContent = '參考匯率更新時間：' + new Date().toLocaleString('zh-TW');
            }
        });
    }
    
    /**
     * 初始化
     */
    async function init() {
        try {
            const result = await convertAll();
            showExchangeInfo(result);
            console.log('匯率轉換完成:', result);
        } catch (error) {
            console.error('匯率轉換失敗:', error);
        }
    }
    
    // DOM 載入完成後執行
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
    
    // 暴露到全域（除錯用）
    window.ExchangeRate = {
        convertAll,
        fetchExchangeRate,
        formatTWD,
        formatZAR
    };
})();