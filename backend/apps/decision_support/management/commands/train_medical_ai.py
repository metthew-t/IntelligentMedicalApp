"""
Django Management Command to Train Medical AI Classifier on 50,000+ Patient Cases.
Usage:
    python manage.py train_medical_ai [--samples 52500] [--export-csv path/to/file.csv]
"""
import os
from django.core.management.base import BaseCommand
from apps.decision_support.ml_engine.model_trainer import MedicalModelTrainer


class Command(BaseCommand):
    help = 'Train the Clinical Decision Support ML Model on 50,000+ realistic patient encounters'

    def add_arguments(self, parser):
        parser.add_argument(
            '--samples',
            type=int,
            default=52500,
            help='Total number of patient encounters to generate and train on (default: 52500)'
        )
        parser.add_argument(
            '--test-size',
            type=float,
            default=0.2,
            help='Fraction of dataset reserved for evaluation testing (default: 0.2)'
        )
        parser.add_argument(
            '--export-csv',
            type=str,
            default=None,
            help='Optional path to export generated training data as a CSV file'
        )

    def handle(self, *args, **options):
        samples = options['samples']
        test_size = options['test_size']
        export_csv = options['export_csv']

        self.stdout.write(self.style.NOTICE("=" * 70))
        self.stdout.write(self.style.NOTICE(" CLINICAL DECISION SUPPORT SYSTEM - ML MODEL TRAINING PIPELINE"))
        self.stdout.write(self.style.NOTICE(f" Target Dataset Size: {samples:,} synthetic patient encounters"))
        self.stdout.write(self.style.NOTICE("=" * 70))

        trainer = MedicalModelTrainer()
        metrics = trainer.train(
            total_samples=samples,
            test_size=test_size,
            export_csv_path=export_csv
        )

        self.stdout.write(self.style.SUCCESS("\n[+] Training & Evaluation Summary:"))
        self.stdout.write(f"    - Total Generated Encounters: {metrics['total_samples']:,}")
        self.stdout.write(f"    - Training Encounters:        {metrics['train_samples']:,}")
        self.stdout.write(f"    - Evaluation Encounters:      {metrics['test_samples']:,}")
        self.stdout.write(f"    - Target Disease Classes:     {metrics['num_diseases']}")
        self.stdout.write(f"    - Input Features:             {metrics['num_features']}")
        self.stdout.write(f"    - Train Accuracy:             {metrics['train_accuracy']*100:.2f}%")
        self.stdout.write(self.style.SUCCESS(f"    - Test Top-1 Accuracy:        {metrics['test_top1_accuracy']*100:.2f}%"))
        self.stdout.write(self.style.SUCCESS(f"    - Test Top-3 Accuracy:        {metrics['test_top3_accuracy']*100:.2f}%"))
        self.stdout.write(self.style.SUCCESS(f"    - Test Top-5 Accuracy:        {metrics['test_top5_accuracy']*100:.2f}%"))
        self.stdout.write(f"    - Total Pipeline Time:        {metrics['total_pipeline_time_sec']}s")
        self.stdout.write(self.style.SUCCESS("\n[OK] Model successfully trained and deployed for diagnostic inference!"))
