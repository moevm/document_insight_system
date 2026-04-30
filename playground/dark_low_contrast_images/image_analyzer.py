"""
Анализатор изображений для проекторов
Определяет, будет ли изображение плохо видно на проекторе

Основные проблемы проектора:
- Низкий контраст
- Темные цвета
- Мелкие детали теряются
- Размытые изображения плохо видно
"""

import cv2
import numpy as np
import os
from pathlib import Path


class ProjectorImageAnalyzer:
    def __init__(self):
        # Минимальная средняя яркость (0-255).
        self.min_brightness = 100 
        
        # Минимальный контраст
        self.min_contrast = 50 
        
        # Минимальная средняя насыщенность
        self.min_saturation = 40 
        
        # Процент темных пикселей
        self.max_dark_pixels_percent = 35 
        
        # Минимальная разница между 10% самых темных и 10% самых светлых пикселей
        self.min_dynamic_range = 100
        
        # Минимальная резкость краев для читаемости текста/кода
        self.min_edge_strength = 12
        self.warning_edge_strength = 15
        
        # Минимальная дисперсия яркости
        self.min_brightness_variance = 1000
        
        # Минимальный локальный контраст
        self.min_local_contrast = 30
        self.excellent_local_contrast = 70 
    
    def load_image(self, image_path):
        image = cv2.imread(image_path)
        
        if image is None:
            print(f"Ошибка: не удалось загрузить изображение {image_path}")
            return None
        
        print(f"Загружено изображение: {os.path.basename(image_path)}")
        print(f"Размер: {image.shape[1]}x{image.shape[0]} пикселей")
        
        return image
    
    def calculate_brightness(self, image):
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        brightness_channel = hsv[:, :, 2]
        avg_brightness = np.mean(brightness_channel)
        return avg_brightness
    
    def calculate_contrast(self, image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        contrast = np.std(gray)
        return contrast
    
    def calculate_saturation(self, image):
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        saturation_channel = hsv[:, :, 1]
        avg_saturation = np.mean(saturation_channel)
        return avg_saturation
    
    def calculate_dark_pixels_percentage(self, image):
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        brightness_channel = hsv[:, :, 2]
        dark_mask = brightness_channel < 50
        
        dark_pixels = np.sum(dark_mask)
        total_pixels = brightness_channel.size

        dark_percentage = (dark_pixels / total_pixels) * 100        
        
        return dark_percentage
    
    def calculate_dynamic_range(self, image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        p10 = np.percentile(gray, 10)
        p90 = np.percentile(gray, 90)
        
        dynamic_range = p90 - p10
        
        return dynamic_range
    
    def calculate_edge_strength(self, image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        
        magnitude = np.sqrt(sobelx**2 + sobely**2)
        edge_strength = np.mean(magnitude)
        
        return edge_strength
    
    def calculate_brightness_variance(self, image):
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        brightness_channel = hsv[:, :, 2]
        variance = np.var(brightness_channel)
        return variance
    
    def calculate_local_contrast(self, image, block_size=50):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        h, w = gray.shape
        
        local_contrasts = []
        
        for i in range(0, h - block_size, block_size):
            for j in range(0, w - block_size, block_size):
                block = gray[i:i+block_size, j:j+block_size]
                block_contrast = np.max(block) - np.min(block)
                local_contrasts.append(block_contrast)
        
        avg_local_contrast = np.mean(local_contrasts) if local_contrasts else 0
        return avg_local_contrast
    
    def check_color_distinguishability(self, image):
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        hue_channel = hsv[:, :, 0]
        saturation_channel = hsv[:, :, 1]
        
        saturated_mask = saturation_channel > 50
        
        if np.sum(saturated_mask) < 100:
            return True, "Мало цветных областей"
        
        hues = hue_channel[saturated_mask]
        
        red_hues = ((hues < 10) | (hues > 170)).sum()
        green_hues = ((hues > 40) & (hues < 80)).sum()
        
        total_colored = len(hues)
        
        if red_hues > total_colored * 0.1 and green_hues > total_colored * 0.1:
            return False, "Используются красный и зеленый (проблема дальтонизма)"
        
        return True, "Цвета различимы"
    
    def analyze_image(self, image_path):
        image = self.load_image(image_path)
        if image is None:
            return None
        
        print("\n" + "="*60)
        print(f"Анализ изображения: {os.path.basename(image_path)}")
        print("="*60)
        
        brightness = self.calculate_brightness(image)
        contrast = self.calculate_contrast(image)
        saturation = self.calculate_saturation(image)
        dark_pixels = self.calculate_dark_pixels_percentage(image)
        dynamic_range = self.calculate_dynamic_range(image)
        edge_strength = self.calculate_edge_strength(image)
        brightness_variance = self.calculate_brightness_variance(image)
        local_contrast = self.calculate_local_contrast(image)
        color_ok, color_msg = self.check_color_distinguishability(image)
        
        is_grayscale = saturation < 10
        image_type = "Ч/Б" if is_grayscale else "Цветное"
        
        print(f"\nТип изображения: {image_type}")
        print(f"\nМетрики изображения:")
        print(f"  Яркость:               {brightness:.1f} (мин: {self.min_brightness})")
        print(f"  Контраст (глобальный): {contrast:.1f} (мин: {self.min_contrast})")
        print(f"  Контраст (локальный):  {local_contrast:.1f} (мин: {self.min_local_contrast}) ВАЖНО")
        
        if not is_grayscale:
            print(f"  Насыщенность:          {saturation:.1f} (мин: {self.min_saturation})")
        
        print(f"  Темные пиксели:        {dark_pixels:.1f}% (макс: {self.max_dark_pixels_percent}%)")
        print(f"  Динамический диапазон: {dynamic_range:.1f} (мин: {self.min_dynamic_range})")
        print(f"  Дисперсия яркости:     {brightness_variance:.1f} (мин: {self.min_brightness_variance})")
        print(f"  Сила краев (резкость): {edge_strength:.1f} (мин: {self.min_edge_strength}) ВАЖНО")
        
        if not is_grayscale:
            print(f"  Различимость цветов:   {color_msg}")
        
        issues = []
        warnings = []
        
        if brightness < self.min_brightness and local_contrast < self.min_local_contrast:
            if is_grayscale:
                issues.append(f"КРИТИЧНО (Ч/Б): Темное и низкий контраст (яркость {brightness:.1f}, контраст {local_contrast:.1f}) - нечитаемо")
            else:
                issues.append(f"КРИТИЧНО: Темное и низкий контраст (яркость {brightness:.1f}, контраст {local_contrast:.1f}) - нечитаемо")
        
        elif local_contrast < self.min_local_contrast:
            if is_grayscale:
                issues.append(f"КРИТИЧНО (Ч/Б): Низкий контраст ({local_contrast:.1f}) - текст сливается с фоном")
            else:
                issues.append(f"КРИТИЧНО: Низкий локальный контраст ({local_contrast:.1f}) - текст плохо различим")
        
        if edge_strength < 10:
            issues.append(f"КРИТИЧНО: Очень размытое ({edge_strength:.1f}) - текст/код абсолютно нечитаем")
        elif edge_strength < self.min_edge_strength:
            issues.append(f"КРИТИЧНО: Размытое ({edge_strength:.1f}) - текст/код может быть нечитаем")
        
        if brightness < self.min_brightness and local_contrast >= self.min_local_contrast:
            if is_grayscale:
                warnings.append(f"Темное Ч/Б ({brightness:.1f}), но контраст хороший - приемлемо для проектора")
            else:
                warnings.append(f"Темное изображение ({brightness:.1f}), но контраст хороший - может быть видно")
        
        if contrast < self.min_contrast:
            if local_contrast >= self.excellent_local_contrast:
                pass
            elif local_contrast >= self.min_local_contrast:
                warnings.append(f"Низкий глобальный контраст ({contrast:.1f}), но локальный контраст приемлем")
        
        if not is_grayscale and saturation < self.min_saturation:
            warnings.append(f"Низкая насыщенность цветов ({saturation:.1f}) - тусклые цвета")
        
        if dark_pixels > self.max_dark_pixels_percent:
            if is_grayscale and local_contrast >= self.min_local_contrast:
                pass
            elif local_contrast < self.min_local_contrast * 1.5:
                warnings.append(f"Много темных пикселей ({dark_pixels:.1f}%) и контраст невысокий")
        
        if dynamic_range < self.min_dynamic_range and brightness_variance > self.min_brightness_variance * 0.5:
            if not is_grayscale: 
                warnings.append(f"Малый динамический диапазон ({dynamic_range:.1f}) - плоское изображение")
        
        if not is_grayscale and brightness_variance < self.min_brightness_variance and local_contrast < self.min_local_contrast:
            warnings.append(f"Низкая дисперсия яркости ({brightness_variance:.1f}) - всё в одном тоне")
        
        if not color_ok and saturation > 20:
            warnings.append(f"{color_msg}")
        
        if edge_strength >= self.min_edge_strength and edge_strength < self.warning_edge_strength:
            warnings.append(f"Резкость немного низкая ({edge_strength:.1f}), может быть проблемой на старых проекторах")
        
        print("\n" + "="*60)
        print("ИТОГОВЫЙ ВЕРДИКТ")
        print("="*60)
        
        if len(issues) == 0 and len(warnings) == 0:
            print("Изображение ОТЛИЧНО ПОДХОДИТ для проектора")
            print("\nВсе метрики в норме:")
            print(f"   • Контраст: {local_contrast:.1f} (отлично)")
            print(f"   • Резкость: {edge_strength:.1f} (отлично)")
            if not is_grayscale:
                print(f"   • Насыщенность: {saturation:.1f} (отлично)")
            verdict = "GOOD"
            
        elif len(issues) == 0:
            print("Изображение ПРИЕМЛЕМО, но есть рекомендации")
            print("\nРекомендации по улучшению:")
            for i, warning in enumerate(warnings, 1):
                print(f"   {i}. {warning}")
            
            # Советы по исправлению
            print("\nКак улучшить:")
            if any('Темное' in w for w in warnings):
                print("  Увеличьте яркость фона или используйте светлую тему")
            if any('насыщенность' in w.lower() for w in warnings):
                print("  Сделайте цвета более яркими/насыщенными")
            if any('динамический' in w.lower() for w in warnings):
                print("  Увеличьте разброс яркостей между элементами")
                
            verdict = "WARNING"
            
        else:
            print("Изображение ПЛОХО ВИДНО на проекторе - ТРЕБУЕТСЯ ИСПРАВЛЕНИЕ")
            print("\nКритичные проблемы (исправьте обязательно):")
            for i, issue in enumerate(issues, 1):
                print(f"   {i}. {issue}")
                
            if warnings:
                print("\nДополнительные проблемы:")
                for i, warning in enumerate(warnings, 1):
                    print(f"   {i}. {warning}")
            
            print("\nКак исправить:")
            if any('контраст' in str(i).lower() for i in issues):
                print("  ОБЯЗАТЕЛЬНО: Увеличьте контраст между текстом и фоном")
                print("  Используйте черный/темно-синий текст на белом фоне")
                print("  Или белый текст на черном/темно-синем фоне")
            if any('Размытое' in str(i) for i in issues):
                print("  ОБЯЗАТЕЛЬНО: Увеличьте резкость или используйте векторный формат")
                print("  Проверьте разрешение изображения (минимум 1024x768)")
            if any('Темное' in str(i) for i in issues):
                print("  ОБЯЗАТЕЛЬНО: Увеличьте контраст (темнота при хорошем контрасте - это OK)")
                
            verdict = "BAD"
        
        print("="*60 + "\n")
        
        return {
            'filename': os.path.basename(image_path),
            'verdict': verdict,
            'brightness': brightness,
            'contrast': contrast,
            'local_contrast': local_contrast,
            'saturation': saturation,
            'dark_pixels_percent': dark_pixels,
            'dynamic_range': dynamic_range,
            'brightness_variance': brightness_variance,
            'edge_strength': edge_strength,
            'color_distinguishable': color_ok,
            'issues': issues,
            'warnings': warnings
        }
    
    def batch_analyze(self, folder_path):
        image_extensions = ['.jpg', '.jpeg', '.png', '.bmp']
        
        folder = Path(folder_path)
        
        if not folder.exists():
            print(f"Ошибка: папка не найдена {folder_path}")
            return []
        
        image_files = [
            str(f) for f in folder.iterdir() 
            if f.is_file() and f.suffix.lower() in image_extensions
        ]
        
        if len(image_files) == 0:
            print(f"Ошибка: в папке {folder_path} не найдено изображений")
            return []
        
        print(f"\nНайдено изображений: {len(image_files)}")
        print("="*60)
        
        results = []
        for image_path in image_files:
            result = self.analyze_image(image_path)
            if result:
                results.append(result)
        
        print("\n" + "="*60)
        print("ИТОГОВАЯ СТАТИСТИКА")
        print("="*60)
        
        good_images = sum(1 for r in results if r['verdict'] == 'GOOD')
        warning_images = sum(1 for r in results if r['verdict'] == 'WARNING')
        bad_images = sum(1 for r in results if r['verdict'] == 'BAD')
        
        print(f"Отлично подходят:      {good_images}")
        print(f"С предупреждениями:    {warning_images}")
        print(f"Плохо видны:           {bad_images}")
        print(f"Всего проанализировано: {len(results)}")
        
        if bad_images > 0:
            print(f"\nИзображения с критичными проблемами:")
            for r in results:
                if r['verdict'] == 'BAD':
                    print(f"  - {r['filename']}: {len(r['issues'])} проблем")
        
        if warning_images > 0:
            print(f"\nИзображения с предупреждениями:")
            for r in results:
                if r['verdict'] == 'WARNING':
                    print(f"  - {r['filename']}: {len(r['warnings'])} предупреждений")
        
        return results


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Анализатор изображений для проектора',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  # Анализ одного изображения
  python image_analyzer.py -i image.jpg
  
  # Анализ всех изображений в папке
  python image_analyzer.py -d ./images
  
  # Анализ с изменением порогов
  python image_analyzer.py -i image.jpg --min-brightness 100 --min-contrast 50
        """
    )
    
    analyzer = ProjectorImageAnalyzer()
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-i', '--image', type=str, help='Путь к одному изображению для анализа')
    group.add_argument('-d', '--directory', type=str, help='Путь к папке с изображениями для пакетного анализа')
    
    parser.add_argument('--min-brightness', type=float, help=f'Минимальная яркость (по умолчанию: {analyzer.min_brightness})')
    parser.add_argument('--min-contrast', type=float, help=f'Минимальный контраст (по умолчанию: {analyzer.min_contrast})')
    parser.add_argument('--min-saturation', type=float, help=f'Минимальная насыщенность (по умолчанию: {analyzer.min_saturation})')
    parser.add_argument('--max-dark-pixels', type=float, help=f'Максимальный процент темных пикселей (по умолчанию: {analyzer.max_dark_pixels_percent})')
    parser.add_argument('--min-dynamic-range', type=float, help=f'Минимальный динамический диапазон (по умолчанию: {analyzer.min_dynamic_range})')
    parser.add_argument('--min-edge-strength', type=float, help=f'Минимальная сила краев (по умолчанию: {analyzer.min_edge_strength})')
    
    args = parser.parse_args()
    
    if args.min_brightness is not None:
        analyzer.min_brightness = args.min_brightness
    if args.min_contrast is not None:
        analyzer.min_contrast = args.min_contrast
    if args.min_saturation is not None:
        analyzer.min_saturation = args.min_saturation
    if args.max_dark_pixels is not None:
        analyzer.max_dark_pixels_percent = args.max_dark_pixels
    if args.min_dynamic_range is not None:
        analyzer.min_dynamic_range = args.min_dynamic_range
    if args.min_edge_strength is not None:
        analyzer.min_edge_strength = args.min_edge_strength
    
    print("="*60)
    print("АНАЛИЗАТОР ИЗОБРАЖЕНИЙ ДЛЯ ПРОЕКТОРА")
    print("="*60)
    
    if args.image:
        analyzer.analyze_image(args.image)
    elif args.directory:
        analyzer.batch_analyze(args.directory)


if __name__ == "__main__":
    main()
