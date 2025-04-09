import { ApplicationConfig } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { provideHttpClient } from '@angular/common/http';
import { AppConfigService } from './app/app-config.service';

export const appConfig: ApplicationConfig = {
  providers: [
    provideHttpClient(),
    {
      provide: 'APP_CONFIG_LOADER',
      useFactory: async () => {
        const http = inject(HttpClient);
        const configService = inject(AppConfigService);

        const config = await firstValueFrom(http.get('/assets/settings.config.json'));
        configService.setConfig(config);
      }
    }
  ]
};
