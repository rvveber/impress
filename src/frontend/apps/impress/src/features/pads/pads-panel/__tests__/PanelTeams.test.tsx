import '@testing-library/jest-dom';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import fetchMock from 'fetch-mock';

import { AppWrapper } from '@/tests/utils';

import { PadList } from '../components/PadList';
import { Panel } from '../components/Panel';

window.HTMLElement.prototype.scroll = function () {};

jest.mock('next/router', () => ({
  ...jest.requireActual('next/router'),
  useRouter: () => ({
    query: {},
  }),
}));

describe('PanelPads', () => {
  afterEach(() => {
    fetchMock.restore();
  });

  it('renders with no pad to display', async () => {
    fetchMock.mock(`/api/pads/?page=1&ordering=-created_at`, {
      count: 0,
      results: [],
    });

    render(<PadList />, { wrapper: AppWrapper });

    expect(screen.getByRole('status')).toBeInTheDocument();

    expect(
      await screen.findByText(
        'Create your first pad by clicking on the "Create a new pad" button.',
      ),
    ).toBeInTheDocument();
  });

  it('renders an empty pad', async () => {
    fetchMock.mock(`/api/pads/?page=1&ordering=-created_at`, {
      count: 1,
      results: [
        {
          id: '1',
          name: 'Team 1',
          accesses: [],
        },
      ],
    });

    render(<PadList />, { wrapper: AppWrapper });

    expect(screen.getByRole('status')).toBeInTheDocument();

    expect(await screen.findByLabelText('Empty pads icon')).toBeInTheDocument();
  });

  it('renders a pad with only 1 member', async () => {
    fetchMock.mock(`/api/pads/?page=1&ordering=-created_at`, {
      count: 1,
      results: [
        {
          id: '1',
          name: 'Team 1',
          accesses: [
            {
              id: '1',
              role: 'owner',
            },
          ],
        },
      ],
    });

    render(<PadList />, { wrapper: AppWrapper });

    expect(screen.getByRole('status')).toBeInTheDocument();

    expect(await screen.findByLabelText('Empty pads icon')).toBeInTheDocument();
  });

  it('renders a non-empty pad', async () => {
    fetchMock.mock(`/api/pads/?page=1&ordering=-created_at`, {
      count: 1,
      results: [
        {
          id: '1',
          name: 'Pad 1',
          accesses: [
            {
              id: '1',
              role: 'admin',
            },
            {
              id: '2',
              role: 'member',
            },
          ],
        },
      ],
    });

    render(<PadList />, { wrapper: AppWrapper });

    expect(screen.getByRole('status')).toBeInTheDocument();

    expect(await screen.findByLabelText('Pads icon')).toBeInTheDocument();
  });

  it('renders the error', async () => {
    fetchMock.mock(`/api/pads/?page=1&ordering=-created_at`, {
      status: 500,
    });

    render(<PadList />, { wrapper: AppWrapper });

    expect(screen.getByRole('status')).toBeInTheDocument();

    expect(
      await screen.findByText(
        'Something bad happens, please refresh the page.',
      ),
    ).toBeInTheDocument();
  });

  it('renders with pad panel open', async () => {
    fetchMock.mock(`/api/pads/?page=1&ordering=-created_at`, {
      count: 1,
      results: [],
    });

    render(<Panel />, { wrapper: AppWrapper });

    expect(
      screen.getByRole('button', { name: 'Close the pads panel' }),
    ).toBeVisible();

    expect(await screen.findByText('Recents')).toBeVisible();
  });

  it('closes and opens the pad panel', async () => {
    fetchMock.mock(`/api/pads/?page=1&ordering=-created_at`, {
      count: 1,
      results: [],
    });

    render(<Panel />, { wrapper: AppWrapper });

    expect(await screen.findByText('Recents')).toBeVisible();

    await userEvent.click(
      screen.getByRole('button', {
        name: 'Close the pads panel',
      }),
    );

    expect(await screen.findByText('Recents')).not.toBeVisible();

    await userEvent.click(
      screen.getByRole('button', {
        name: 'Open the pads panel',
      }),
    );

    expect(await screen.findByText('Recents')).toBeVisible();
  });
});