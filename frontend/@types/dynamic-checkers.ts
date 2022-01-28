import { IEntry, IListEntry, IUser } from '@/types';


export const checkListEntry = (listEntry: any, res?: any): IListEntry => {
  if (
    !!listEntry &&
    !!listEntry.slug && typeof listEntry.slug === 'string' &&
    !!listEntry.title && typeof listEntry.title === 'string' &&
    !!listEntry.created_at && typeof listEntry.created_at === 'string'
  ) {
    const obj: IListEntry = {
      slug: listEntry.slug,
      title: listEntry.title,
      created_at: listEntry.created_at,
    };

    return obj;
  }

  const error = new Error("Failed 'checkListEntry'");
  // error.response = res;
  throw error;
};


export const checkEntry = (entry: any, res?: any): IEntry => {
  if (
    !!entry &&
    !!entry.slug && typeof entry.slug === 'string' &&
    !!entry.title && typeof entry.title === 'string' &&
    !!entry.value && typeof entry.value === 'string' &&
    !!entry.created_at && typeof entry.created_at === 'string'
  ) {
    const obj: IEntry = {
      slug: entry.slug,
      title: entry.title,
      value: entry.value,
      created_at: entry.created_at,
    };

    return obj;
  }

  const error = new Error("Failed 'checkEntry'");
  // error.response = res;
  throw error;
};


export const checkToken = (token: any, res?: any): string => {
  if (!!token && typeof token === 'string' && /^[\w-]{64}$/.test(token)) {
    return token;
  }

  const error = new Error("Failed 'checkToken'");
  // error.response = res;
  throw error;
};


export const checkUser = (user: any, res?: any): IUser => {
  if (
    !!user &&
    !!user.user_slug && typeof user.user_slug === 'string' &&
    !!user.name && typeof user.name === 'string' &&
    !!user.email && typeof user.email === 'string' &&
    typeof user.email_is_verified === 'boolean' &&
    typeof user.phone_number_is_verified === 'boolean' &&
    typeof user.tfa_is_enabled === 'boolean' &&
    typeof user.truncated_phone_number === 'string'
  ) {
    const obj: IUser = {
      user_slug: user.user_slug,
      name: user.name,
      email: user.email,
      email_is_verified: user.email_is_verified,
      phone_number_is_verified: user.phone_number_is_verified,
      tfa_is_enabled: user.tfa_is_enabled,
      truncated_phone_number: user.truncated_phone_number,
    };

    return obj;
  }

  const error = new Error("Failed 'checkUser'");
  // error.response = res;
  throw error;
};