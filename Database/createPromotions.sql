-- Active: 1775030978688@@127.0.0.1@3306@discounts_db
-- Sample data for `promotions` table (MySQL)
-- Based on model: Promotion(id, active, code, start_date, expire_date,
-- promotion_type, availability_count, value, max_discount_amount,
-- min_order_value, description)

INSERT INTO `promotions` (
	`active`,
	`code`,
	`start_date`,
	`expire_date`,
	`promotion_type`,
	`availability_count`,
	`value`,
	`max_discount_amount`,
	`min_order_value`,
	`description`
) VALUES
	(1, 'NEW10',       '2026-03-01 00:00:00', '2026-12-31 23:59:59', 'COUPON', 150, 0.10, 100000,      0, 'Giam 10% cho khach hang moi'),
	(1, 'SAVE15',      '2026-03-10 00:00:00', '2026-11-30 23:59:59', 'COUPON', 120, 0.15, 180000, 300000, 'Giam 15% don tu 300k'),
	(1, 'FLASH20',     '2026-04-01 00:00:00', '2026-04-30 23:59:59', 'COUPON',  80, 0.20, 200000, 500000, 'Flash sale giam 20%'),
	(1, 'VIP25',       '2026-01-01 00:00:00', '2026-12-31 23:59:59', 'COUPON',  60, 0.25, 300000, 800000, 'Uu dai VIP giam 25%'),
	(1, 'WEEKEND5',    '2026-03-01 00:00:00', '2026-08-31 23:59:59', 'COUPON', 200, 0.05,  50000, 100000, 'Cuoi tuan giam 5%'),
	(1, 'MORNING12',   '2026-03-15 00:00:00', '2026-09-30 23:59:59', 'COUPON', 140, 0.12, 120000, 250000, 'Khung gio sang giam 12%'),
	(1, 'APPONLY8',    '2026-02-01 00:00:00', '2026-10-31 23:59:59', 'COUPON', 160, 0.08,  80000, 120000, 'Danh rieng cho don app'),
	(1, 'SUMMER18',    '2026-05-01 00:00:00', '2026-07-31 23:59:59', 'COUPON',  90, 0.18, 220000, 450000, 'Mua he giam 18%'),
	(1, 'LOYAL7',      '2026-01-15 00:00:00', '2026-12-31 23:59:59', 'COUPON', 300, 0.07,  70000, 100000, 'Tri an khach hang than thiet'),
	(1, 'BDAY30',      '2026-01-01 00:00:00', '2026-12-31 23:59:59', 'COUPON',  40, 0.30, 250000, 600000, 'Sinh nhat giam 30%'),

	(1, 'SHIP50K',     '2026-03-01 00:00:00', '2026-12-31 23:59:59', 'VOUCHER', 180,  50000, NULL,      0, 'Voucher 50k cho moi don'),
	(1, 'LESS100K',    '2026-02-15 00:00:00', '2026-09-30 23:59:59', 'VOUCHER', 110, 100000, NULL, 300000, 'Giam truc tiep 100k'),
	(1, 'LESS150K',    '2026-03-20 00:00:00', '2026-10-31 23:59:59', 'VOUCHER',  95, 150000, NULL, 500000, 'Don tren 500k giam 150k'),
	(1, 'LESS200K',    '2026-04-01 00:00:00', '2026-06-30 23:59:59', 'VOUCHER',  70, 200000, NULL, 700000, 'Khuyen mai quy 2 giam 200k'),
	(1, 'BIG300K',     '2026-05-01 00:00:00', '2026-12-31 23:59:59', 'VOUCHER',  50, 300000, NULL, 900000, 'Voucher gia tri lon 300k'),
	(1, 'NIGHT80K',    '2026-03-01 00:00:00', '2026-11-30 23:59:59', 'VOUCHER', 130,  80000, NULL, 250000, 'Khung gio toi giam 80k'),
	(1, 'HOLIDAY120',  '2026-04-10 00:00:00', '2026-12-31 23:59:59', 'VOUCHER', 100, 120000, NULL, 400000, 'Le tet giam 120k'),
	(1, 'PAYDAY90K',   '2026-03-25 00:00:00', '2026-08-31 23:59:59', 'VOUCHER', 115,  90000, NULL, 350000, 'Ngay luong giam 90k'),
	(1, 'FAST60K',     '2026-03-01 00:00:00', '2026-07-31 23:59:59', 'VOUCHER', 145,  60000, NULL, 150000, 'Voucher nhanh 60k'),
	(1, 'FREEDAY110',  '2026-06-01 00:00:00', '2026-12-31 23:59:59', 'VOUCHER',  85, 110000, NULL, 380000, 'Ngay dac biet giam 110k');
