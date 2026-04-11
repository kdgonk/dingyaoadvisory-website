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
    const FALLBACK_RATE = 1.675; // 1 ZAR ≈ 1.675 TWD（2026 年參考值）
    
    /**
     * 格式化數字為台幣格式
     */
    function formatTWD(amount) {
        if (amount >= 10000) {
            return '約 NT$ ' + Math.round(amount / 10000) + ' 萬';
        }
        return 'NT$ ' + Math.round(amount).toLocaleString('zh-TW');
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
        
        console.log('匯率轉換開始，匯率:', rate, 'ZAR/TWD');
        
        // 找出所有需要轉換的元素
        const elements = document.querySelectorAll('[data-zar]');
        console.log('找到 ' + elements.length + ' 個需要轉換的元素');
        
        elements.forEach(el => {
            const zar = parseFloat(el.getAttribute('data-zar'));
            const twd = zar * rate;
            
            // 檢查是否有自定義格式
            const format = el.getAttribute('data-format');
            if (format === 'short') {
                el.textContent = formatTWD(twd);
            } else if (format === 'table') {
                if (twd >= 10000) {
                    el.textContent = 'NT$ ' + Math.round(twd / 10000) + ' 萬';
                } else {
                    el.textContent = 'NT$ ' + Math.round(twd).toLocaleString('zh-TW');
                }
            } else {
                el.textContent = '約新台幣 ' + Math.round(twd / 10000) + ' 萬元';
            }
            
            console.log('轉換:', zar, 'ZAR →', Math.round(twd), 'TWD');
        });
        
        // 更新匯率時間戳記
        const timestampElements = document.querySelectorAll('[data-exchange-time]');
        timestampElements.forEach(el => {
            const time = new Date();
            const formattedTime = time.getFullYear() + '年' + 
                (time.getMonth() + 1) + '月' + 
                time.getDate() + '日 ' +
                time.getHours().toString().padStart(2, '0') + ':' +
                time.getMinutes().toString().padStart(2, '0');
            el.textContent = '參考匯率時間：' + formattedTime + '（1 ZAR ≈ ' + rate.toFixed(4) + ' TWD）';
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
     * 初始化
     */
    async function init() {
        try {
            const result = await convertAll();
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
        formatTWD
    };
})();