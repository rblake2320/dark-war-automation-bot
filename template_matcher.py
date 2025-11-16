"""
Template matching system for game UI elements
"""

import cv2
import numpy as np
import os
import logging
from typing import Optional, Tuple, List
from dataclasses import dataclass

@dataclass
class TemplateMatch:
    x: int
    y: int
    confidence: float
    template_name: str

class TemplateMatcher:
    def __init__(self, templates_dir: str = "templates", threshold: float = 0.8):
        self.templates_dir = templates_dir
        self.threshold = threshold
        self.templates = {}
        self.logger = logging.getLogger(__name__)
        self.load_templates()

    def load_templates(self):
        """Load all template images from templates directory"""
        if not os.path.exists(self.templates_dir):
            os.makedirs(self.templates_dir)
            self.logger.warning(f"Templates directory created: {self.templates_dir}")
            return

        for filename in os.listdir(self.templates_dir):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                template_path = os.path.join(self.templates_dir, filename)
                template = cv2.imread(template_path, cv2.IMREAD_COLOR)
                if template is not None:
                    template_name = os.path.splitext(filename)[0]
                    self.templates[template_name] = template
                    self.logger.debug(f"Loaded template: {template_name}")

        self.logger.info(f"Loaded {len(self.templates)} templates")

    def find_template(self, screenshot: np.ndarray, template_name: str) -> Optional[TemplateMatch]:
        """Find a specific template in the screenshot"""
        if template_name not in self.templates:
            self.logger.warning(f"Template not found: {template_name}")
            return None

        template = self.templates[template_name]

        try:
            # Perform template matching
            result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

            if max_val >= self.threshold:
                x, y = max_loc
                return TemplateMatch(x, y, max_val, template_name)
            else:
                self.logger.debug(f"Template {template_name} not found (confidence: {max_val:.3f})")
                return None

        except Exception as e:
            self.logger.error(f"Error matching template {template_name}: {e}")
            return None

    def find_all_templates(self, screenshot: np.ndarray) -> List[TemplateMatch]:
        """Find all templates in the screenshot"""
        matches = []

        for template_name in self.templates:
            match = self.find_template(screenshot, template_name)
            if match:
                matches.append(match)

        return matches

    def get_template_center(self, match: TemplateMatch) -> Tuple[int, int]:
        """Get center coordinates of a template match"""
        if match.template_name not in self.templates:
            return match.x, match.y

        template = self.templates[match.template_name]
        height, width = template.shape[:2]
        center_x = match.x + width // 2
        center_y = match.y + height // 2

        return center_x, center_y

    def save_template_from_screenshot(self, screenshot: np.ndarray,
                                    x: int, y: int, width: int, height: int,
                                    template_name: str):
        """Save a region of the screenshot as a new template"""
        try:
            # Extract the region
            template = screenshot[y:y+height, x:x+width]

            # Save to templates directory
            template_path = os.path.join(self.templates_dir, f"{template_name}.png")
            cv2.imwrite(template_path, template)

            # Add to loaded templates
            self.templates[template_name] = template

            self.logger.info(f"Saved template: {template_name} at {template_path}")

        except Exception as e:
            self.logger.error(f"Error saving template {template_name}: {e}")

    def test_all_templates(self, screenshot: np.ndarray) -> dict:
        """Test all templates and return results"""
        results = {}

        for template_name in self.templates:
            match = self.find_template(screenshot, template_name)
            results[template_name] = {
                'found': match is not None,
                'confidence': match.confidence if match else 0.0,
                'position': (match.x, match.y) if match else None
            }

        return results